"""scripts/release_notes.py writes one CHANGELOG section and never falls back."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/release_notes.py"

CHANGELOG = """# Changelog

## Unreleased

- Not released yet.

## 0.2.0 - 2026-12-01

- Second release.

## [0.1.0]

- First release.
"""


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("release_notes", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release_notes = load_script()


def test_a_section_is_returned_up_to_the_next_heading() -> None:
    assert release_notes.release_notes(CHANGELOG, "0.2.0") == "- Second release.\n"
    assert release_notes.release_notes(CHANGELOG, "0.1.0") == "- First release.\n"


def test_a_version_with_no_section_fails_and_never_uses_unreleased() -> None:
    with pytest.raises(ValueError, match=r"no section for 0\.3\.0"):
        release_notes.release_notes(CHANGELOG, "0.3.0")


def test_a_version_prefix_does_not_match_a_longer_version() -> None:
    with pytest.raises(ValueError, match=r"no section for 0\.2$"):
        release_notes.release_notes(CHANGELOG, "0.2")


def test_an_empty_section_fails() -> None:
    with pytest.raises(ValueError, match="is empty"):
        release_notes.release_notes("## 1.0.0\n\n## 0.9.0\n\n- Old.\n", "1.0.0")


def test_main_writes_the_file_or_exits_non_zero_with_a_clear_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(CHANGELOG, encoding="utf-8")
    out = tmp_path / "notes.md"
    assert release_notes.main(["x", "0.2.0", str(changelog), str(out)]) == 0
    assert out.read_text(encoding="utf-8") == "- Second release.\n"
    assert release_notes.main(["x", "9.9.9", str(changelog), str(tmp_path / "none.md")]) == 1
    assert "CHANGELOG.md has no section for 9.9.9" in capsys.readouterr().err
    assert not (tmp_path / "none.md").exists()
    assert release_notes.main(["x"]) == 2
