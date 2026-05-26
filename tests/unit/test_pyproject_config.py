"""Tests for pyproject.toml configuration (T02 verification).

Validates that pyproject.toml exists, is valid TOML, and contains
all required sections per the project's code style and testing conventions.
"""

import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


def _load_pyproject() -> dict:
    """Load pyproject.toml and return the parsed dict."""
    return tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))


class TestPyprojectToml:
    """pyproject.toml must be valid and contain all required sections."""

    def test_pyproject_toml_exists_and_is_valid(self) -> None:
        """pyproject.toml must be valid TOML at the project root."""
        assert PYPROJECT_PATH.is_file(), "pyproject.toml is missing"
        data = _load_pyproject()
        assert isinstance(data, dict), "pyproject.toml did not parse to a dict"

    def test_project_section_exists(self) -> None:
        """[project] section must exist with basic metadata."""
        data = _load_pyproject()
        project = data.get("project", {})
        assert project, "[project] section is missing"
        assert "name" in project, "[project] is missing 'name'"
        assert "version" in project, "[project] is missing 'version'"
        assert "requires-python" in project, (
            "[project] is missing 'requires-python'"
        )

    def test_python_version_is_at_least_3_12(self) -> None:
        """Python requirement must be >= 3.12."""
        data = _load_pyproject()
        requires_python = data["project"]["requires-python"]
        assert "3.12" in requires_python or "3.13" in requires_python, (
            f"requires-python is {requires_python!r}, expected >=3.12"
        )

    def test_ruff_config_exists(self) -> None:
        """[tool.ruff] section must be configured."""
        data = _load_pyproject()
        ruff = data.get("tool", {}).get("ruff", {})
        assert ruff, "[tool.ruff] section is missing"
        assert "line-length" in ruff, "[tool.ruff] is missing 'line-length'"
        assert ruff.get("line-length") == 88, (
            f"Expected line-length=88, got {ruff.get('line-length')}"
        )

    def test_ruff_lint_config_exists(self) -> None:
        """[tool.ruff.lint] section must be configured."""
        data = _load_pyproject()
        lint = data.get("tool", {}).get("ruff", {}).get("lint", {})
        assert lint, "[tool.ruff.lint] section is missing"
        select = lint.get("select", [])
        # Must include at least basic rules
        assert "E" in select, "ruff lint 'select' missing 'E' (pycodestyle errors)"
        assert "F" in select, "ruff lint 'select' missing 'F' (Pyflakes)"
        assert "I" in select, "ruff lint 'select' missing 'I' (isort)"

    def test_mypy_config_exists(self) -> None:
        """[tool.mypy] section must be configured with strict mode."""
        data = _load_pyproject()
        mypy = data.get("tool", {}).get("mypy", {})
        assert mypy, "[tool.mypy] section is missing"
        assert mypy.get("strict") is True, (
            "[tool.mypy] strict must be True"
        )
        assert mypy.get("python_version") == "3.12", (
            f"mypy python_version should be 3.12, got {mypy.get('python_version')}"
        )

    def test_pytest_config_exists(self) -> None:
        """[tool.pytest.ini_options] section must be configured."""
        data = _load_pyproject()
        pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
        assert pytest_opts, "[tool.pytest.ini_options] section is missing"
        assert "addopts" in pytest_opts, "pytest addopts is missing"
        assert "testpaths" in pytest_opts, "pytest testpaths is missing"
        assert pytest_opts.get("testpaths") == ["tests"], (
            f"testpaths should be ['tests'], got {pytest_opts.get('testpaths')}"
        )

    def test_coverage_config_exists(self) -> None:
        """[tool.coverage.run] and [tool.coverage.report] must be configured."""
        data = _load_pyproject()
        coverage = data.get("tool", {}).get("coverage", {})
        assert coverage, "[tool.coverage] section is missing"

        run_config = coverage.get("run", {})
        assert run_config, "[tool.coverage.run] is missing"
        assert "source" in run_config, "coverage source is not configured"
        assert "app" in run_config.get("source", []), (
            "coverage source must include 'app'"
        )

        report_config = coverage.get("report", {})
        assert report_config, "[tool.coverage.report] is missing"
        assert "fail_under" in report_config, "coverage fail_under is not set"
        assert report_config.get("fail_under") == 80, (
            f"coverage fail_under should be 80, got {report_config.get('fail_under')}"
        )

    def test_ruff_format_config_exists(self) -> None:
        """[tool.ruff.format] section must exist."""
        data = _load_pyproject()
        fmt = data.get("tool", {}).get("ruff", {}).get("format", {})
        assert fmt, "[tool.ruff.format] section is missing"
