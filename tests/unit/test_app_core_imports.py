"""Tests verifying the Dependency Rule: app/core/ has zero external imports.

Per DDD and Clean Architecture, the domain layer (app/core/) must never
depend on infrastructure concerns like SQLAlchemy, FastAPI, or HTTP libraries.
"""

import ast
import sys
from collections.abc import Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = PROJECT_ROOT / "app" / "core"

# External libraries that MUST NOT appear in app/core/
FORBIDDEN_IMPORTS = {
    "sqlalchemy",
    "fastapi",
    "starlette",  # FastAPI foundation
    "uvicorn",
    "http",
    "httpx",
    "requests",
    "urllib",
    "psycopg2",
    "alembic",
    "pydantic_settings",
}

# Standard library modules — detected at runtime (requires Python 3.10+)
_STDLIB = set(sys.stdlib_module_names)


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
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports


def _find_violations(
    checker: Callable[[Path, set[str]], str | None],
) -> list[str]:
    """Scan core files and collect violation messages.

    Args:
        checker: Called with (file_path, file_imports) for each .py file.
                 Returns a violation message string, or None if the file is clean.

    Returns:
        List of violation messages for files that failed the check.
    """
    violations: list[str] = []
    for py_file in _collect_python_files(CORE_DIR):
        file_imports = _extract_imports(py_file)
        msg = checker(py_file, file_imports)
        if msg:
            violations.append(msg)
    return violations


def _relative_path(py_file: Path) -> str:
    """Return a file path relative to the project root for error messages."""
    return str(py_file.relative_to(PROJECT_ROOT))


class TestCoreLayerImports:
    """The domain layer (app/core/) must have zero external dependencies."""

    def test_core_directory_exists(self) -> None:
        """Sanity check: app/core/ must exist."""
        assert CORE_DIR.is_dir(), f"{CORE_DIR} does not exist"

    def test_no_sqlalchemy_imports_in_core(self) -> None:
        """app/core/ must not import anything from SQLAlchemy."""
        violations = _find_violations(
            lambda f, imports: (
                f"{_relative_path(f)} imports sqlalchemy"
                if "sqlalchemy" in imports
                else None
            )
        )
        assert not violations, (
            "SQLAlchemy imports found in domain layer:\n" + "\n".join(violations)
        )

    def test_no_fastapi_imports_in_core(self) -> None:
        """app/core/ must not import anything from FastAPI."""
        violations = _find_violations(
            lambda f, imports: (
                f"{_relative_path(f)} imports fastapi" if "fastapi" in imports else None
            )
        )
        assert not violations, "FastAPI imports found in domain layer:\n" + "\n".join(
            violations
        )

    def test_no_forbidden_external_imports_in_core(self) -> None:
        """app/core/ must not import any forbidden external library."""
        violations = _find_violations(
            lambda f, imports: (
                f"{_relative_path(f)} imports: {sorted(imports & FORBIDDEN_IMPORTS)}"
                if imports & FORBIDDEN_IMPORTS
                else None
            )
        )
        assert not violations, (
            "Forbidden external imports in domain layer:\n" + "\n".join(violations)
        )

    def test_core_only_imports_stdlib_and_itself(self) -> None:
        """app/core/ should only import stdlib modules and other core modules.

        This validates that no third-party packages sneak into the domain layer
        through indirect imports or typo-level imports.
        """
        allowed = _STDLIB | {"core"} | {"__future__"} | {"app"}

        violations = _find_violations(
            lambda f, imports: (
                # Skip files with no imports (module-level docstrings only)
                None
                if not imports
                else (
                    f"{_relative_path(f)} imports non-stdlib: {sorted(imports - allowed)}"
                    if imports - allowed
                    else None
                )
            )
        )
        assert not violations, (
            "Non-stdlib imports in domain layer (only stdlib allowed):\n"
            + "\n".join(violations)
        )
