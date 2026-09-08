# Proposal: Deterministic Unit Test Generation

## Task Summary

The agent must build a self-contained test generation harness that produces comprehensive
pytest test suites for five target modules, covering all statement and branch paths.
The system reads task specifications from `data/test_specs.json`, copies template test
files from `data/templates/` to `tests/generated/`, runs pytest with `--cov-branch`
to measure both statement and branch coverage, and emits a structured JSON report
with full provenance metadata.

Coverage threshold is 80% for both statement and branch coverage per target module.

Five target modules are covered: **Stack** (OOP), **fibonacci** (algorithm),
**flatten** (algorithm), **BinarySearchTree** (OOP), and **text_stats** (utilities).

---

## Key Components

### 1. Instruction Specification (`instruction.md`)

Create `/workspace/run_test_gen.py` supporting:

| Flag | Description |
|------|-------------|
| `--specs <path>` | Path to `test_specs.json` |
| `--task <id\|all>` | Task to generate (default: `all`) |
| `--out <path>` | Output directory for generated test files |
| `--format [json\|text]` | Report format |
| `--skip-coverage` | Skip pytest-cov run (generation only) |

**Retrieval Rules:**
- Match each task spec by `task_id` to its template in `data/templates/test_<task_id>.py`.
- Copy template verbatim to `tests/generated/test_<task_id>.py`.
- Run `pytest --cov=<target_module> --cov-branch --cov-report=json` per task.
- Parse `totals.percent_covered` for statement coverage and `covered_branches/num_branches` for branch coverage.
- Attach provenance: `task_id`, `spec_id`, `test_count`, `sha256`, `timestamp`, `statement_coverage`, `branch_coverage`.

**Answer Rules:**
- Return `{"status": "no_data"}` when spec file is missing or malformed.
- Return `{"status": "no_data"}` when no tasks match the `--task` argument.
- Never fabricate coverage percentages — all values must come from real pytest-cov JSON output.
- Mark generation as `status: error` when a template file is missing.

---

### 2. Environment Setup (`Dockerfile`)

**Base Image:** `python:3.11-slim`

**Installed Packages:**
```
numpy>=1.26.0
pytest>=8.0.0
pytest-cov>=4.1.0
coverage>=7.3.0
python-dotenv>=1.0.0
```

**Fixtures pre-loaded at build time:**
```
/workspace/targets/          — five target Python modules
/workspace/data/test_specs.json
/workspace/data/templates/   — five comprehensive test templates
/workspace/eval/tasks/       — per-task constraints
```

**Failing baseline state:** `prepare_data.py` runs at build time, installing stub tests
in `tests/generated/` and a pre-computed low-coverage `reports/test_report.json`:

| Task | Stmt % | Branch % |
|------|--------|----------|
| stack | 30.0 | 0.0 |
| fibonacci | 62.5 | 50.0 |
| flatten | 62.5 | 33.3 |
| binary_tree | 28.6 | 8.3 |
| text_stats | 25.0 | 0.0 |

All below the 80% threshold — `eval.py` fails on T5 and T6 before `solve.sh` runs.

Environment knobs:

| Variable | Default | Purpose |
|----------|---------|---------|
| `TGEN_DEVICE` | `cpu` | Compute device |
| `TGEN_SEED` | `42` | Reproducibility seed |
| `TGEN_MODE` | `full` | Generation mode |
| `TGEN_COVERAGE_THRESHOLD` | `0.80` | Min coverage (80%) |
| `TGEN_MAX_TESTS` | `50` | Max tests per task |

---

### 3. Reference Golden Solution (`solve.sh` / `run_test_gen.py`)

1. Read `test_specs.json` — resolve all 5 task specs.
2. For each task, locate `data/templates/test_<task_id>.py`.
3. Copy template bytes verbatim to `tests/generated/test_<task_id>.py`.
4. Compute SHA256 of generated file (for determinism proof).
5. Run `pytest tests/generated/test_<task_id>.py --cov=<target_module> --cov-branch --cov-report=json:<path>`.
6. Parse coverage JSON — extract `totals.percent_covered` and branch percentage.
7. Emit per-task report entry with full provenance.
8. Write `reports/test_report.json`.

---

### 4. Automated Deterministic Evaluation (`eval.py`)

| Test | What it checks |
|------|---------------|
| **T1 — Spec retrieval** | All 5 task_ids in spec; all 5 templates exist; all 5 generated files exist |
| **T2 — Multi-source coverage** | test_report.json has statement_coverage, branch_coverage, test_count for all tasks |
| **T3 — Fault tolerance** | Missing spec → no_data; malformed JSON → no_data; missing template → status=error |
| **T4 — Determinism** | Re-generate all 5 files, SHA256 byte-identical to originals |
| **T5 — Edge case coverage** | pytest.raises present (exception targets); base cases present; all required function calls present |
| **T6 — Branch & statement ≥ 80%** | Reads test_report.json; all tasks pass threshold |
| **T7 — Empty/malformed spec** | `{}`, `{"tasks":[]}`, missing path → no tasks returned, no crash |
| **T8 — Metadata provenance** | Report has spec_id, timestamp, coverage_threshold; each task has task_id, spec_id, test_count, statement_coverage, branch_coverage, all_tests_passed, timestamp |

---

## Verification Plan

```bash
docker build -t tgen-task .
docker run --rm tgen-task python eval.py    # FAIL (stubs, low coverage)
docker run --rm tgen-task bash solve.sh     # exit 0
docker run --rm tgen-task python eval.py    # PASS (exit 0)
```
