import tomllib
from pathlib import Path

PYPROJECT = tomllib.loads(
    (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
)


def test_exclude_newer_pilot_and_python_version() -> None:
    assert PYPROJECT["tool"]["uv"]["exclude-newer"] == "7 days"
    assert PYPROJECT["project"]["requires-python"] == ">=3.14"


def test_mypy_is_strict_on_the_package_and_the_scripts() -> None:
    assert PYPROJECT["tool"]["mypy"]["strict"] is True
    assert PYPROJECT["tool"]["mypy"]["files"] == ["src/project_template", "scripts"]


def test_coverage_floor_is_at_least_85_percent_on_the_package() -> None:
    addopts = PYPROJECT["tool"]["pytest"]["ini_options"]["addopts"]
    assert "--cov=project_template" in addopts
    floor = int(addopts.split("--cov-fail-under=")[1].split()[0])
    assert floor >= 85


def test_ruff_matches_the_baseline_block() -> None:
    # REPO-03: dropping a rule family (for example S) must fail a test, not only weaken lint.
    ruff = PYPROJECT["tool"]["ruff"]
    assert ruff["line-length"] == 100
    assert ruff["target-version"] == "py314"
    assert ruff["lint"]["select"] == ["E", "F", "W", "I", "B", "UP", "S", "SIM", "RUF", "T20"]
    assert ruff["lint"]["per-file-ignores"] == {"tests/**": ["S101"]}


def test_cli_script_and_exact_pins() -> None:
    assert PYPROJECT["project"]["scripts"] == {"pt": "project_template.cli:app"}
    pins = PYPROJECT["project"]["dependencies"] + PYPROJECT["dependency-groups"]["dev"]
    assert all("==" in pin for pin in pins)
