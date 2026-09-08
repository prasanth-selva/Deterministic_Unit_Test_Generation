# Deterministic Unit Test Generation — Task Specification

## Task

Implement `/workspace/run_test_gen.py` to generate comprehensive pytest test suites
for five target modules, measure branch and statement coverage with pytest-cov, and
emit a structured report meeting the 80% coverage threshold for all targets.

## Working Directory

`/workspace`

## Required Outputs

| Path | Description |
|------|-------------|
| `tests/generated/test_<task_id>.py` | Comprehensive generated test file (×5) |
| `reports/test_report.json` | Coverage report with full provenance |
| `eval/results.json` | Binary evaluation report (8 tests) |

## Entry Points

```bash
chmod +x solve.sh && ./solve.sh
```

Or individually:

```bash
python prepare_data.py
python run_test_gen.py --task all --format json
python eval.py
```

## CLI Reference — `run_test_gen.py`

| Flag | Default | Description |
|------|---------|-------------|
| `--specs` | `data/test_specs.json` | Spec file path |
| `--task` | `all` | Task ID or `all` |
| `--out` | `tests/generated/` | Output directory |
| `--format` | `json` | `json` or `text` |
| `--skip-coverage` | off | Skip pytest-cov run |

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `TGEN_DEVICE` | `cpu` | Compute device |
| `TGEN_SEED` | `42` | Reproducibility seed |
| `TGEN_MODE` | `full` | Generation mode |
| `TGEN_COVERAGE_THRESHOLD` | `0.80` | Min coverage (80%) |
| `TGEN_MAX_TESTS` | `50` | Max tests per task |

## Test Report Schema (`test_report.json`)

```json
{
  "spec_id": "TGEN-SPEC-001",
  "timestamp": "<ISO 8601 UTC>",
  "coverage_threshold": 0.80,
  "mode": "full",
  "tasks": [
    {
      "task_id": "<snake_case>",
      "spec_id": "<TGEN-NNN>",
      "test_file": "tests/generated/test_<task_id>.py",
      "test_count": <int>,
      "sha256": "<hex>",
      "statement_coverage": <float 0-100>,
      "branch_coverage": <float 0-100>,
      "all_tests_passed": <bool>,
      "timestamp": "<ISO 8601 UTC>"
    }
  ]
}
```

## Constraints

- No network calls inside any Python module.
- All configuration via environment variables — no hardcoded values.
- `eval.py` must exit code `0` if all 8 tests pass, non-zero otherwise.
- When spec file is missing or malformed, return `{"status": "no_data"}`.
- Never fabricate coverage percentages — values must come from real pytest-cov output.
- All 5 generated test files must achieve ≥ 80% statement AND branch coverage.
- Generated test files must be byte-identical on repeated generation (determinism).
- Tests must cover: exception paths (pytest.raises), empty inputs, base cases.
