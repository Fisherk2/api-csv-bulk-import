"""Tests for the DDD directory structure (T01 verification).

These tests ensure the directory layout defined in docs/ARCHITECTURE.md exists
and that every package has a proper __init__.py with a docstring.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Directories that MUST exist (from docs/ARCHITECTURE.md)
REQUIRED_DIRECTORIES = [
    "app",
    "app/core",
    "app/core/entities",
    "app/core/repositories",
    "app/core/services",
    "app/infrastructure",
    "app/infrastructure/database",
    "app/infrastructure/database/models",
    "app/infrastructure/repositories",
    "app/infrastructure/auth",
    "app/infrastructure/api",
    "app/infrastructure/api/endpoints",
    "app/schemas",
    "app/utils",
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "migrations",
    "migrations/versions",
]


class TestDirectoryStructure:
    """Verify all required directories exist."""

    def test_all_app_directories_exist(self) -> None:
        """Every directory in the architecture spec must be present."""
        missing = [
            d for d in REQUIRED_DIRECTORIES
            if not (PROJECT_ROOT / d).is_dir()
        ]
        assert not missing, (
            f"Missing directories: {missing}"
        )

    def test_every_python_package_has_init_py(self) -> None:
        """Every Python package must have an __init__.py with a docstring.

        Excludes directories that are not Python packages:
        - migrations/versions/ stores Alembic migration files, not Python modules.
        """
        non_package_dirs = {"migrations/versions"}
        failures: list[str] = []
        for dir_rel in REQUIRED_DIRECTORIES:
            if dir_rel in non_package_dirs:
                continue
            init_file = PROJECT_ROOT / dir_rel / "__init__.py"
            if not init_file.is_file():
                failures.append(f"Missing __init__.py: {dir_rel}")
                continue
            content = init_file.read_text(encoding="utf-8").strip()
            if not content:
                failures.append(f"Empty __init__.py (no docstring): {dir_rel}")

        assert not failures, (
            "__init__.py issues:\n" + "\n".join(failures)
        )

    def test_migrations_versions_has_gitkeep(self) -> None:
        """migrations/versions/ must have a .gitkeep file."""
        gitkeep = PROJECT_ROOT / "migrations" / "versions" / ".gitkeep"
        assert gitkeep.exists(), (
            "migrations/versions/.gitkeep is missing"
        )

    def test_app_directory_count_matches_spec(self) -> None:
        """The number of app/ directories should match the architecture spec."""
        app_root = PROJECT_ROOT / "app"
        actual_dirs = sorted(
            str(p.relative_to(PROJECT_ROOT))
            for p in app_root.rglob("*")
            if p.is_dir()
        )
        expected_app_dirs = [
            d for d in REQUIRED_DIRECTORIES if d.startswith("app")
        ]
        unexpected = set(actual_dirs) - set(expected_app_dirs)
        assert not unexpected, (
            f"Unexpected directories under app/: {sorted(unexpected)}"
        )

    def test_all_init_files_have_meaningful_docstrings(self) -> None:
        """Every __init__.py docstring must be more than a trivial placeholder."""
        trivial = ('"""__init__.py"""', '"""init"""', '"""package"""', '""""""')
        failures: list[str] = []
        for dir_rel in REQUIRED_DIRECTORIES:
            init_file = PROJECT_ROOT / dir_rel / "__init__.py"
            if not init_file.is_file():
                continue
            content = init_file.read_text(encoding="utf-8").strip()
            if content in trivial:
                failures.append(
                    f"Trivial docstring in {dir_rel}/__init__.py: {content}"
                )

        assert not failures, (
            "Docstrings should describe the package purpose:\n"
            + "\n".join(failures)
        )
