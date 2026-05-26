"""Tests verifying the Dependency Rule: app/core/ has zero external imports.

Per DDD and Clean Architecture, the domain layer (app/core/) must never
depend on infrastructure concerns like SQLAlchemy, FastAPI, or HTTP libraries.
"""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = PROJECT_ROOT / "app" / "core"

# External libraries that MUST NOT appear in app/core/
FORBIDDEN_IMPORTS = {
    "sqlalchemy",
    "fastapi",
    "starlette",        # FastAPI foundation
    "uvicorn",
    "http",
    "httpx",
    "requests",
    "urllib",
    "psycopg2",
    "alembic",
    "pydantic_settings",
}


def _collect_python_files(root: Path) -> list[Path]:
    """Recursively collect all .py files under a directory."""
    return sorted(root.rglob("*.py"))


def _extract_imports(file_path: Path) -> set[str]:
    """Parse a Python file and return all top-level module names imported."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Get the top-level module (e.g., "sqlalchemy.orm" → "sqlalchemy")
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports


class TestCoreLayerImports:
    """The domain layer (app/core/) must have zero external dependencies."""

    def test_core_directory_exists(self) -> None:
        """Sanity check: app/core/ must exist."""
        assert CORE_DIR.is_dir(), f"{CORE_DIR} does not exist"

    def test_no_sqlalchemy_imports_in_core(self) -> None:
        """app/core/ must not import anything from SQLAlchemy."""
        violations: list[str] = []
        for py_file in _collect_python_files(CORE_DIR):
            file_imports = _extract_imports(py_file)
            if "sqlalchemy" in file_imports:
                rel = py_file.relative_to(PROJECT_ROOT)
                violations.append(f"{rel} imports sqlalchemy")
        assert not violations, (
            "SQLAlchemy imports found in domain layer:\n"
            + "\n".join(violations)
        )

    def test_no_fastapi_imports_in_core(self) -> None:
        """app/core/ must not import anything from FastAPI."""
        violations: list[str] = []
        for py_file in _collect_python_files(CORE_DIR):
            file_imports = _extract_imports(py_file)
            if "fastapi" in file_imports:
                rel = py_file.relative_to(PROJECT_ROOT)
                violations.append(f"{rel} imports fastapi")
        assert not violations, (
            "FastAPI imports found in domain layer:\n"
            + "\n".join(violations)
        )

    def test_no_forbidden_external_imports_in_core(self) -> None:
        """app/core/ must not import any forbidden external library."""
        violations: list[str] = []
        for py_file in _collect_python_files(CORE_DIR):
            file_imports = _extract_imports(py_file)
            forbidden_found = file_imports & FORBIDDEN_IMPORTS
            if forbidden_found:
                rel = py_file.relative_to(PROJECT_ROOT)
                violations.append(
                    f"{rel} imports: {sorted(forbidden_found)}"
                )
        assert not violations, (
            "Forbidden external imports in domain layer:\n"
            + "\n".join(violations)
        )

    def test_core_only_imports_stdlib_and_itself(self) -> None:
        """app/core/ should only import stdlib modules and other core modules.

        This validates that no third-party packages sneak into the domain layer
        through indirect imports or typo-level imports.
        """
        # Standard library top-level modules (detected at runtime via sys)
        # sys.stdlib_module_names is available since Python 3.10
        stdlib_top_level = set(sys.stdlib_module_names)

        # Our own packages that core may reference
        own_packages = {"core"}
        allowed = stdlib_top_level | own_packages | {"__future__"}

        violations: list[str] = []
        for py_file in _collect_python_files(CORE_DIR):
            file_imports = _extract_imports(py_file)
            # Module-level __init__ docstrings only — no imports at all is fine
            if not file_imports:
                continue
            unexpected = file_imports - allowed
            if unexpected:
                rel = py_file.relative_to(PROJECT_ROOT)
                violations.append(
                    f"{rel} imports non-stdlib: {sorted(unexpected)}"
                )

        assert not violations, (
            "Non-stdlib imports in domain layer (only stdlib allowed):\n"
            + "\n".join(violations)
        )
