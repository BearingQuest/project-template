"""core/ is pure: it imports only the standard library and project_template itself."""

import ast
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parents[1] / "src/project_template/core"
# core may use the shared error types and its own package, nothing else here.
ALLOWED_PACKAGE_IMPORTS = ("project_template.core", "project_template.errors")


def imported_modules(path: Path) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, f"{path.name}: relative import"
            assert node.module
            modules.append(node.module)
    return modules


def test_core_has_python_files() -> None:
    assert list(CORE.glob("*.py"))


def test_core_imports_only_the_standard_library_and_its_own_package() -> None:
    for path in CORE.rglob("*.py"):
        for module in imported_modules(path):
            top = module.split(".")[0]
            if top in sys.stdlib_module_names:
                continue
            assert module in ALLOWED_PACKAGE_IMPORTS or module.startswith(
                "project_template.core"
            ), f"{path.name} imports {module}"


def test_core_does_no_io_and_imports_no_infrastructure() -> None:
    banned = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "pathlib",
        "logging",
        "typer",
        "pydantic_settings",
    }
    for path in CORE.rglob("*.py"):
        assert not banned & {m.split(".")[0] for m in imported_modules(path)}, path.name
        assert "project_template.config" not in imported_modules(path), path.name
        assert "project_template.logging_setup" not in imported_modules(path), path.name
        assert "project_template.cli" not in imported_modules(path), path.name
