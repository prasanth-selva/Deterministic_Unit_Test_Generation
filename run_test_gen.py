from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config
import generator
import runner


def load_specs_from(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "no_data", "reason": f"spec file not found: {path}"}
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        return {"status": "no_data", "reason": f"invalid JSON: {exc}"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Deterministic Unit Test Generation — branch and statement coverage"
    )
    p.add_argument("--specs", default=str(config.SPECS_FILE))
    p.add_argument("--task", default="all")
    p.add_argument("--out", default=str(config.GENERATED_DIR))
    p.add_argument("--format", default="json", choices=["json", "text"])
    p.add_argument("--skip-coverage", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    specs_path = Path(args.specs)
    out_dir = Path(args.out)

    specs_data = load_specs_from(specs_path)
    if specs_data.get("status") == "no_data":
        print(json.dumps(specs_data, indent=2))
        return

    tasks = generator.resolve_tasks(specs_data, args.task)
    if not tasks:
        resp = {"status": "no_data", "reason": f"no tasks matched '{args.task}'"}
        print(json.dumps(resp, indent=2))
        return

    gen_results = generator.generate_all(tasks, out_dir)

    task_reports: list[dict[str, Any]] = []
    for spec, gen in zip(tasks, gen_results):
        if gen.get("status") != "ok":
            task_reports.append({
                "task_id": spec["task_id"],
                "spec_id": spec["spec_id"],
                "test_count": 0,
                "statement_coverage": 0.0,
                "branch_coverage": 0.0,
                "all_tests_passed": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": gen.get("reason", "generation_failed"),
            })
            continue

        if args.skip_coverage:
            existing_cov = {}
            if config.TEST_REPORT_FILE.exists():
                try:
                    with open(config.TEST_REPORT_FILE) as rf:
                        existing_report = json.load(rf)
                    for t in existing_report.get("tasks", []):
                        if t.get("task_id") == spec["task_id"]:
                            existing_cov = t
                            break
                except Exception:
                    pass
            cov_result: dict[str, Any] = {
                "statement_coverage": existing_cov.get("statement_coverage", 0.0),
                "branch_coverage": existing_cov.get("branch_coverage", 0.0),
                "all_tests_passed": existing_cov.get("all_tests_passed", False),
            }
        else:
            cov_result = runner.run_coverage(
                spec["task_id"],
                Path(gen["out_path"]),
                spec["target_module"],
            )

        task_reports.append({
            "task_id": spec["task_id"],
            "spec_id": spec["spec_id"],
            "test_file": gen["out_path"],
            "test_count": gen["test_count"],
            "sha256": gen["sha256"],
            "statement_coverage": cov_result.get("statement_coverage", 0.0),
            "branch_coverage": cov_result.get("branch_coverage", 0.0),
            "all_tests_passed": cov_result.get("all_tests_passed", False),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    report: dict[str, Any] = {
        "spec_id": specs_data.get("spec_id", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "coverage_threshold": config.TGEN_COVERAGE_THRESHOLD,
        "mode": config.TGEN_MODE,
        "tasks": task_reports,
    }

    if not args.skip_coverage:
        config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(config.TEST_REPORT_FILE, "w") as f:
            json.dump(report, f, indent=2)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        threshold_pct = config.TGEN_COVERAGE_THRESHOLD * 100
        for entry in task_reports:
            stmt = entry["statement_coverage"]
            br = entry["branch_coverage"]
            verdict = "PASS" if stmt >= threshold_pct and br >= threshold_pct else "FAIL"
            print(
                f"[{verdict}] {entry['task_id']}: "
                f"stmt={stmt:.1f}%  branch={br:.1f}%  "
                f"tests={entry['test_count']}"
            )


if __name__ == "__main__":
    main()
