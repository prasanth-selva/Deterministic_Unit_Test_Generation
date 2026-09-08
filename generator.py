from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import config


def load_specs() -> dict[str, Any]:
    if not config.SPECS_FILE.exists():
        return {"status": "no_data", "reason": f"spec file not found: {config.SPECS_FILE}"}
    try:
        with open(config.SPECS_FILE) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        return {"status": "no_data", "reason": f"invalid JSON: {exc}"}


def resolve_tasks(specs_data: dict[str, Any], task_arg: str) -> list[dict[str, Any]]:
    tasks = specs_data.get("tasks", [])
    if task_arg == "all":
        return tasks
    return [t for t in tasks if t["task_id"] == task_arg]


def template_path(task_id: str) -> Path:
    return config.TEMPLATES_DIR / f"test_{task_id}.py"


def generated_path(task_id: str, out_dir: Path) -> Path:
    return out_dir / f"test_{task_id}.py"


def count_test_functions(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        tree = ast.parse(path.read_text())
        return sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        )
    except SyntaxError:
        return 0


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_task(spec: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    task_id = spec["task_id"]
    tmpl = template_path(task_id)
    out = generated_path(task_id, out_dir)

    if not tmpl.exists():
        return {
            "task_id": task_id,
            "spec_id": spec["spec_id"],
            "status": "error",
            "reason": f"template not found: {tmpl}",
        }

    out_dir.mkdir(parents=True, exist_ok=True)
    out.write_bytes(tmpl.read_bytes())

    return {
        "task_id": task_id,
        "spec_id": spec["spec_id"],
        "template": str(tmpl),
        "out_path": str(out),
        "test_count": count_test_functions(out),
        "sha256": file_sha256(out),
        "status": "ok",
    }


def generate_all(
    tasks: list[dict[str, Any]],
    out_dir: Path,
) -> list[dict[str, Any]]:
    return [generate_task(spec, out_dir) for spec in tasks]
