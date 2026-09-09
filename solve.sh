#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  PYTHON=python
fi

PY=${PYTHON:-python3}
if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
fi

if ! "$PY" -c "import pytest_cov" >/dev/null 2>&1; then
  echo "==> Installing required coverage dependencies"
  "$PY" -m pip install --quiet -r requirements.txt
fi

echo "==> Writing stub (low-coverage) test files — failing baseline"
"$PY" prepare_data.py

echo "==> Generating comprehensive test suites from templates"
"$PY" run_test_gen.py --task all --format json

echo "==> Text summary of coverage results"
"$PY" run_test_gen.py --task all --format text --skip-coverage

echo "==> Running evaluation suite"
"$PY" eval.py

echo "==> Done. Report at reports/test_report.json and eval/results.json"
