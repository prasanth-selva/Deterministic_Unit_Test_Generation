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

if [ ! -d ".venv" ]; then
  echo "==> Creating virtualenv"
  "$PYTHON" -m venv .venv
fi

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
  PY=python
elif [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
  PY=python
else
  PY="$PYTHON"
fi

echo "==> Installing dependencies"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet numpy pytest pytest-cov coverage python-dotenv

echo "==> Writing stub (low-coverage) test files — failing baseline"
"$PY" prepare_data.py

echo "==> Generating comprehensive test suites from templates"
"$PY" run_test_gen.py --task all --format json

echo "==> Text summary of coverage results"
"$PY" run_test_gen.py --task all --format text --skip-coverage

echo "==> Running evaluation suite"
"$PY" eval.py

echo "==> Done. Report at reports/test_report.json and eval/results.json"
