import tomllib
from pathlib import Path

PYPROJECT = tomllib.loads(
    (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
)


def test_exclude_newer_pilot_and_python_version() -> None:
    assert PYPROJECT["tool"]["uv"]["exclude-newer"] == "7 days"
    assert PYPROJECT["project"]["requires-python"] == ">=3.14"


def test_mypy_is_strict_on_the_package() -> None:
    assert PYPROJECT["tool"]["mypy"]["strict"] is True
    assert PYPROJECT["tool"]["mypy"]["files"] == ["src/project_template"]


def test_coverage_floor_is_at_least_85_percent_on_the_package() -> None:
    addopts = PYPROJECT["tool"]["pytest"]["ini_options"]["addopts"]
    assert "--cov=project_template" in addopts
    floor = int(addopts.split("--cov-fail-under=")[1].split()[0])
    assert floor >= 85


def test_cli_script_and_exact_pins() -> None:
    assert PYPROJECT["project"]["scripts"] == {"pt": "project_template.cli:app"}
    pins = PYPROJECT["project"]["dependencies"] + PYPROJECT["dependency-groups"]["dev"]
    assert all("==" in pin for pin in pins)
