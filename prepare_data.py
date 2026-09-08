from __future__ import annotations

import json
from pathlib import Path

import config

STUBS: dict[str, str] = {
    "stack": (
        "from targets.stack import Stack\n\n\n"
        "def test_push_basic():\n"
        "    s = Stack()\n"
        "    s.push(1)\n"
        "    assert s.size() == 1\n"
    ),
    "fibonacci": (
        "from targets.fibonacci import fibonacci\n\n\n"
        "def test_fibonacci_basic():\n"
        "    assert fibonacci(5) == 5\n"
    ),
    "flatten": (
        "from targets.flatten import flatten\n\n\n"
        "def test_flatten_basic():\n"
        "    assert flatten([1, [2, 3]]) == [1, 2, 3]\n"
    ),
    "binary_tree": (
        "from targets.binary_tree import BinarySearchTree\n\n\n"
        "def test_insert_root():\n"
        "    bst = BinarySearchTree()\n"
        "    bst.insert(10)\n"
        "    assert bst.root.value == 10\n"
    ),
    "text_stats": (
        "from targets.text_stats import word_count\n\n\n"
        "def test_word_count_basic():\n"
        "    assert word_count(\"hello world\") == 2\n"
    ),
}

STUB_COVERAGE_REPORT: dict = {
    "spec_id": "TGEN-SPEC-001",
    "timestamp": "2026-09-08T00:00:00+00:00",
    "coverage_threshold": config.TGEN_COVERAGE_THRESHOLD,
    "mode": "stub",
    "tasks": [
        {
            "task_id": "stack",
            "spec_id": "TGEN-001",
            "test_count": 1,
            "statement_coverage": 30.0,
            "branch_coverage": 0.0,
            "all_tests_passed": True,
            "timestamp": "2026-09-08T00:00:00+00:00",
        },
        {
            "task_id": "fibonacci",
            "spec_id": "TGEN-002",
            "test_count": 1,
            "statement_coverage": 62.5,
            "branch_coverage": 50.0,
            "all_tests_passed": True,
            "timestamp": "2026-09-08T00:00:00+00:00",
        },
        {
            "task_id": "flatten",
            "spec_id": "TGEN-003",
            "test_count": 1,
            "statement_coverage": 62.5,
            "branch_coverage": 33.3,
            "all_tests_passed": True,
            "timestamp": "2026-09-08T00:00:00+00:00",
        },
        {
            "task_id": "binary_tree",
            "spec_id": "TGEN-004",
            "test_count": 1,
            "statement_coverage": 28.6,
            "branch_coverage": 8.3,
            "all_tests_passed": True,
            "timestamp": "2026-09-08T00:00:00+00:00",
        },
        {
            "task_id": "text_stats",
            "spec_id": "TGEN-005",
            "test_count": 1,
            "statement_coverage": 25.0,
            "branch_coverage": 0.0,
            "all_tests_passed": True,
            "timestamp": "2026-09-08T00:00:00+00:00",
        },
    ],
}


def main() -> None:
    if not config.SPECS_FILE.exists():
        raise SystemExit(f"Specs file not found: {config.SPECS_FILE}")

    config.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    for task_id, stub_code in STUBS.items():
        out = config.GENERATED_DIR / f"test_{task_id}.py"
        out.write_text(stub_code)
        print(f"Wrote stub: {out}")

    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.TEST_REPORT_FILE, "w") as f:
        json.dump(STUB_COVERAGE_REPORT, f, indent=2)
    print(f"Wrote stub coverage report: {config.TEST_REPORT_FILE}")


if __name__ == "__main__":
    main()
