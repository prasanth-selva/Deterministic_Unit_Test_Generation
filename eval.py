from __future__ import annotations

import ast
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import config
import generator
from run_test_gen import load_specs_from


def load_all_specs() -> list[dict[str, Any]]:
    data = load_specs_from(config.SPECS_FILE)
    if data.get("status") == "no_data":
        return []
    return data.get("tasks", [])


def t1_spec_retrieval() -> tuple[bool, str]:
    specs = load_all_specs()
    found_ids = {s["task_id"] for s in specs}

    missing_from_spec = [t for t in config.TASK_IDS if t not in found_ids]
    if missing_from_spec:
        return False, f"T1 FAIL: task_ids missing from spec: {missing_from_spec}"

    missing_templates = [
        t for t in config.TASK_IDS
        if not (config.TEMPLATES_DIR / f"test_{t}.py").exists()
    ]
    if missing_templates:
        return False, f"T1 FAIL: template files missing: {missing_templates}"

    missing_generated = [
        t for t in config.TASK_IDS
        if not (config.GENERATED_DIR / f"test_{t}.py").exists()
    ]
    if missing_generated:
        return False, f"T1 FAIL: generated files missing: {missing_generated}"

    return True, f"T1 PASS: all {len(config.TASK_IDS)} specs, templates, and generated files present"


def t2_multi_source_coverage() -> tuple[bool, str]:
    if not config.TEST_REPORT_FILE.exists():
        return False, f"T2 FAIL: test_report.json not found at {config.TEST_REPORT_FILE}"

    with open(config.TEST_REPORT_FILE) as f:
        report = json.load(f)

    tasks = report.get("tasks", [])
    required_fields = {
        "statement_coverage", "branch_coverage", "test_count", "all_tests_passed"
    }
    sources_present: set[str] = set()
    failures: list[str] = []

    for entry in tasks:
        for field in required_fields:
            if field in entry:
                sources_present.add(field)
            else:
                failures.append(f"{entry.get('task_id', '?')}: missing '{field}'")
        if entry.get("all_tests_passed") is not True:
            failures.append(f"{entry.get('task_id', '?')}: generated tests did not pass")

    if not required_fields.issubset(sources_present):
        missing = required_fields - sources_present
        return False, f"T2 FAIL: coverage sources not all present: missing={missing}"

    if failures:
        return False, f"T2 FAIL: missing fields: {failures}"

    return True, (
        f"T2 PASS: all sources active={sources_present} "
        f"across {len(tasks)} tasks"
    )


def t3_fault_tolerance() -> tuple[bool, str]:
    missing_path = config.ROOT / "_nonexistent_specs_xyz.json"
    result = load_specs_from(missing_path)
    if result.get("status") != "no_data":
        return False, f"T3 FAIL: missing spec should return no_data, got={result}"

    malformed_path = config.ROOT / "_malformed_specs_test.json"
    malformed_path.write_text("{{ not valid json !!!")
    result2 = load_specs_from(malformed_path)
    if result2.get("status") != "no_data":
        return False, f"T3 FAIL: malformed JSON should return no_data, got={result2}"

    missing_tmpl = generator.template_path("_nonexistent_task_xyz")
    fake_spec = {"spec_id": "X-001", "task_id": "_nonexistent_task_xyz", "target_module": "x"}
    gen_result = generator.generate_task(fake_spec, config.GENERATED_DIR)
    if gen_result.get("status") != "error":
        return False, f"T3 FAIL: missing template should return status=error, got={gen_result}"

    return True, "T3 PASS: missing spec, malformed JSON, and missing template all handled gracefully"


def t4_determinism() -> tuple[bool, str]:
    specs = load_all_specs()
    if not specs:
        return False, "T4 FAIL: no specs loaded"

    temp_dir = config.ROOT / "_determinism_verify_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    mismatches: list[str] = []
    for spec in specs:
        task_id = spec["task_id"]
        original = config.GENERATED_DIR / f"test_{task_id}.py"
        if not original.exists():
            mismatches.append(f"{task_id}: original generated file not found")
            continue

        gen2_result = generator.generate_task(spec, temp_dir)
        if gen2_result.get("status") != "ok":
            mismatches.append(f"{task_id}: re-generation failed: {gen2_result.get('reason')}")
            continue

        hash1 = generator.file_sha256(original)
        hash2 = gen2_result["sha256"]

        if hash1 != hash2:
            mismatches.append(
                f"{task_id}: SHA256 mismatch "
                f"(original={hash1[:12]}... re-generated={hash2[:12]}...)"
            )

    if mismatches:
        return False, f"T4 FAIL: determinism violated: {mismatches}"

    return True, f"T4 PASS: all {len(specs)} generated files are byte-identical on re-generation"


def t5_edge_case_coverage() -> tuple[bool, str]:
    specs = load_all_specs()
    failures: list[str] = []

    for spec in specs:
        task_id = spec["task_id"]
        path = config.GENERATED_DIR / f"test_{task_id}.py"
        if not path.exists():
            failures.append(f"{task_id}: generated file not found")
            continue
        content = path.read_text()

        constraints = spec.get("constraints", {})

        required_raises = constraints.get("must_cover_raises", [])
        if required_raises and "pytest.raises" not in content:
            failures.append(f"{task_id}: must_cover_raises={required_raises} but no pytest.raises found")

        required_base_cases = constraints.get("must_cover_base_cases", [])
        for base_case in required_base_cases:
            if base_case not in content:
                failures.append(f"{task_id}: base case '{base_case}' not found in test file")

        required_calls = constraints.get("required_function_calls", [])
        for fn_name in required_calls:
            if fn_name not in content:
                failures.append(f"{task_id}: required call '{fn_name}' not found in test file")

        forbidden = constraints.get("forbidden_substrings", [])
        for substr in forbidden:
            if substr in content:
                failures.append(f"{task_id}: forbidden substring '{substr}' found in test file")

    if failures:
        return False, f"T5 FAIL: edge case coverage violations: {failures}"
    return True, "T5 PASS: all edge cases, base cases, and required calls present in every generated test file"


def t6_branch_statement_coverage() -> tuple[bool, str]:
    if not config.TEST_REPORT_FILE.exists():
        return (
            False,
            f"T6 FAIL: test_report.json not found at {config.TEST_REPORT_FILE} "
            "(run run_test_gen.py first)",
        )

    with open(config.TEST_REPORT_FILE) as f:
        report = json.load(f)

    threshold_pct = config.TGEN_COVERAGE_THRESHOLD * 100
    tasks = report.get("tasks", [])
    failures: list[str] = []

    for entry in tasks:
        task_id = entry.get("task_id", "?")
        stmt = entry.get("statement_coverage", 0.0)
        br = entry.get("branch_coverage", 0.0)

        if stmt < threshold_pct:
            failures.append(
                f"{task_id}: statement_coverage={stmt:.1f}% < {threshold_pct:.0f}%"
            )
        if br < threshold_pct:
            failures.append(
                f"{task_id}: branch_coverage={br:.1f}% < {threshold_pct:.0f}%"
            )

    if len(tasks) < len(config.TASK_IDS):
        failures.append(
            f"only {len(tasks)}/{len(config.TASK_IDS)} tasks in report"
        )

    if failures:
        return False, f"T6 FAIL: coverage below {threshold_pct:.0f}% threshold: {failures}"

    return (
        True,
        f"T6 PASS: all {len(tasks)} tasks ≥ {threshold_pct:.0f}% "
        f"statement and branch coverage",
    )


def t7_empty_malformed_spec() -> tuple[bool, str]:
    empty_path = config.ROOT / "_empty_spec_tgen_test.json"
    empty_path.write_text("{}")
    result = load_specs_from(empty_path)
    tasks = generator.resolve_tasks(result, "all")
    if tasks:
        return False, f"T7 FAIL: empty spec should yield no tasks, got={tasks}"

    no_tasks_path = config.ROOT / "_no_tasks_tgen_test.json"
    no_tasks_path.write_text('{"tasks": []}')
    result2 = load_specs_from(no_tasks_path)
    tasks2 = generator.resolve_tasks(result2, "all")
    if tasks2:
        return False, f"T7 FAIL: spec with empty tasks list should yield no tasks"

    nonexistent_path = config.ROOT / "_completely_missing_tgen_spec.json"
    result3 = load_specs_from(nonexistent_path)
    if result3.get("status") != "no_data":
        return False, f"T7 FAIL: nonexistent spec should return no_data, got={result3}"

    return True, "T7 PASS: empty, empty-tasks, and missing specs all handled without crash"


def t8_metadata_provenance() -> tuple[bool, str]:
    if not config.TEST_REPORT_FILE.exists():
        return (
            False,
            f"T8 FAIL: test_report.json not found at {config.TEST_REPORT_FILE} "
            "(run run_test_gen.py first)",
        )

    with open(config.TEST_REPORT_FILE) as f:
        report = json.load(f)

    top_level_required = ["spec_id", "timestamp", "coverage_threshold", "tasks"]
    missing_top = [f for f in top_level_required if f not in report]
    if missing_top:
        return False, f"T8 FAIL: top-level fields missing: {missing_top}"

    task_required = [
        "task_id", "spec_id", "test_count",
        "statement_coverage", "branch_coverage",
        "all_tests_passed", "timestamp",
    ]
    failures: list[str] = []

    for entry in report.get("tasks", []):
        for field in task_required:
            if field not in entry:
                failures.append(f"{entry.get('task_id', '?')}: missing '{field}'")

        if "spec_id" in entry and not entry["spec_id"].startswith("TGEN-"):
            failures.append(
                f"{entry.get('task_id', '?')}: spec_id format unexpected: {entry['spec_id']}"
            )

    if len(report.get("tasks", [])) < len(config.TASK_IDS):
        failures.append(
            f"only {len(report.get('tasks', []))}/{len(config.TASK_IDS)} tasks in report"
        )

    if failures:
        return False, f"T8 FAIL: provenance failures: {failures}"

    return (
        True,
        f"T8 PASS: full provenance — "
        f"spec_id={report['spec_id']}, "
        f"threshold={report['coverage_threshold']}, "
        f"tasks={len(report['tasks'])} with all required fields",
    )


TESTS = [
    ("T1: Spec retrieval & file tracing", t1_spec_retrieval),
    ("T2: Multi-source coverage reporting", t2_multi_source_coverage),
    ("T3: Fault tolerance", t3_fault_tolerance),
    ("T4: Determinism (SHA256 stability)", t4_determinism),
    ("T5: Edge case coverage", t5_edge_case_coverage),
    ("T6: Branch & statement coverage ≥ threshold", t6_branch_statement_coverage),
    ("T7: Empty/malformed spec handling", t7_empty_malformed_spec),
    ("T8: Metadata provenance", t8_metadata_provenance),
]


def main() -> None:
    results: list[dict[str, Any]] = []
    all_pass = True

    for name, fn in TESTS:
        try:
            passed, msg = fn()
        except Exception as exc:
            passed = False
            msg = f"EXCEPTION: {exc}"
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"[{status}] {name}: {msg}")
        results.append({"test": name, "status": status, "message": msg})

    config.EVAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.RESULTS_FILE, "w") as f:
        json.dump(
            {"tests": results, "overall": "PASS" if all_pass else "FAIL"},
            f,
            indent=2,
        )

    print(f"\nResults → {config.RESULTS_FILE}")
    print(f"Overall: {'PASS' if all_pass else 'FAIL'}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
