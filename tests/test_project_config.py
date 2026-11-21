import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_TEXT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
PYPROJECT = tomllib.loads(PYPROJECT_TEXT)


def tool_uv_head() -> tuple[list[str], str]:
    """The lines between the [tool.uv] header and its first key, and that key's line."""
    lines = PYPROJECT_TEXT.splitlines()
    start = lines.index("[tool.uv]") + 1
    between: list[str] = []
    for line in lines[start:]:
        if line.strip() and not line.lstrip().startswith("#"):
            return between, line
        between.append(line)
    raise AssertionError("[tool.uv] has no key")


def test_exclude_newer_pilot_and_python_version() -> None:
    assert PYPROJECT["tool"]["uv"]["exclude-newer"] == "7 days"
    assert PYPROJECT["project"]["requires-python"] == ">=3.14"


def test_exclude_newer_is_the_first_key_under_tool_uv() -> None:
    _, first_key = tool_uv_head()
    assert first_key == 'exclude-newer = "7 days"'


def test_no_bracket_between_the_tool_uv_header_and_exclude_newer() -> None:
    # Semgrep reads the table only up to the first bracket.
    between, _ = tool_uv_head()
    assert not any("[" in line or "]" in line for line in between)


def test_lock_records_the_seven_day_span() -> None:
    lock = (ROOT / "uv.lock").read_text(encoding="utf-8")
    assert 'exclude-newer-span = "P7D"' in lock.splitlines()


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
