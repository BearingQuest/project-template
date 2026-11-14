"""`make sbom` describes the locked runtime dependencies, and nothing dev-only."""

from __future__ import annotations

import json
import shlex
import tomllib
from pathlib import Path
from typing import Any

from _proc import run

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = {"typer", "pydantic", "pydantic-settings"}


def sbom_command(out: Path) -> list[str]:
    """The `uv export` line of the Makefile's sbom recipe, writing to `out`."""
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    recipe = makefile.split("\nsbom:", 1)[1].split("\n\n", 1)[0]
    line = next(line.strip() for line in recipe.splitlines() if "uv export" in line)
    command = shlex.split(line)
    command[command.index("-o") + 1] = str(out)
    return command


def dev_group_names() -> set[str]:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return {pin.split("==", 1)[0].lower() for pin in pyproject["dependency-groups"]["dev"]}


def component_names(tmp_path: Path) -> tuple[dict[str, Any], set[str]]:
    out = tmp_path / "sbom.cdx.json"
    run(sbom_command(out), cwd=ROOT, check=True, capture_output=True)
    data: dict[str, Any] = json.loads(out.read_text(encoding="utf-8"))
    return data, {str(c["name"]).lower() for c in data["components"]}


def test_sbom_is_cyclonedx_json_of_the_runtime_packages(tmp_path: Path) -> None:
    data, names = component_names(tmp_path)
    assert data["bomFormat"] == "CycloneDX"
    assert data["specVersion"] == "1.5"
    assert names >= RUNTIME


def test_no_dev_group_package_is_in_the_sbom(tmp_path: Path) -> None:
    _, names = component_names(tmp_path)
    dev = dev_group_names()
    assert {"pytest", "ruff", "mypy", "pip-audit"} <= dev
    assert not dev & names, dev & names


def test_the_sbom_recipe_exports_locked_runtime_dependencies_only() -> None:
    command = sbom_command(Path("out.json"))
    assert "--locked" in command and "--no-dev" in command and "--no-emit-project" in command
    assert "cyclonedx1.5" in command
