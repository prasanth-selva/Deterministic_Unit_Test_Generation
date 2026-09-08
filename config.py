from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).parent

TGEN_DEVICE = os.getenv("TGEN_DEVICE", "cpu")
TGEN_SEED = int(os.getenv("TGEN_SEED", "42"))
TGEN_MODE = os.getenv("TGEN_MODE", "full")
TGEN_COVERAGE_THRESHOLD = float(os.getenv("TGEN_COVERAGE_THRESHOLD", "0.80"))
TGEN_MAX_TESTS = int(os.getenv("TGEN_MAX_TESTS", "50"))

DATA_DIR = ROOT / "data"
SPECS_FILE = DATA_DIR / "test_specs.json"
TEMPLATES_DIR = DATA_DIR / "templates"

TARGETS_DIR = ROOT / "targets"

TESTS_DIR = ROOT / "tests"
GENERATED_DIR = TESTS_DIR / "generated"

REPORTS_DIR = ROOT / "reports"
TEST_REPORT_FILE = REPORTS_DIR / "test_report.json"

EVAL_DIR = ROOT / "eval"
EVAL_TASKS_DIR = EVAL_DIR / "tasks"
RESULTS_FILE = EVAL_DIR / "results.json"

TASK_IDS = ["stack", "fibonacci", "flatten", "binary_tree", "text_stats"]
