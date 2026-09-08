from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import config


def _parse_coverage_json(report_path: Path) -> dict[str, float]:
    if not report_path.exists():
        return {"statement_coverage": 0.0, "branch_coverage": 0.0, "parse_error": True}
    try:
        with open(report_path) as f:
            data = json.load(f)
        totals = data.get("totals", {})
        stmt_pct = float(totals.get("percent_covered", 0.0))
        covered_br = int(totals.get("covered_branches", 0))
        num_br = int(totals.get("num_branches", 0))
        branch_pct = (covered_br / num_br * 100.0) if num_br > 0 else 100.0
        return {
            "statement_coverage": round(stmt_pct, 2),
            "branch_coverage": round(branch_pct, 2),
            "covered_lines": totals.get("covered_lines", 0),
            "num_statements": totals.get("num_statements", 0),
            "covered_branches": covered_br,
            "num_branches": num_br,
        }
    except (json.JSONDecodeError, KeyError, TypeError):
        return {"statement_coverage": 0.0, "branch_coverage": 0.0, "parse_error": True}


def run_coverage(
    task_id: str,
    test_path: Path,
    target_module: str,
) -> dict[str, Any]:
    if not test_path.exists():
        return {
            "task_id": task_id,
            "status": "error",
            "reason": f"test file not found: {test_path}",
            "all_tests_passed": False,
            "statement_coverage": 0.0,
            "branch_coverage": 0.0,
        }

    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    cov_json = config.REPORTS_DIR / f"coverage_{task_id}.json"

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_path),
        f"--cov={target_module}",
        "--cov-branch",
        f"--cov-report=json:{cov_json}",
        "-q",
        "--tb=short",
        "--no-header",
    ]

    result = subprocess.run(
        cmd,
        cwd=config.ROOT,
        capture_output=True,
        text=True,
    )

    passed = result.returncode == 0
    cov = _parse_coverage_json(cov_json)

    return {
        "task_id": task_id,
        "target_module": target_module,
        "all_tests_passed": passed,
        "statement_coverage": cov.get("statement_coverage", 0.0),
        "branch_coverage": cov.get("branch_coverage", 0.0),
        "covered_lines": cov.get("covered_lines", 0),
        "num_statements": cov.get("num_statements", 0),
        "covered_branches": cov.get("covered_branches", 0),
        "num_branches": cov.get("num_branches", 0),
        "stdout": result.stdout[-800:] if result.stdout else "",
    }
