"""Tests for the project Makefile (T02 verification).

Validates that the Makefile exists, is not empty, and contains
all required targets as specified in tasks/plan.md Task 2.
"""

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"

# Required targets from tasks/plan.md Task 2
REQUIRED_TARGETS = [
    "help",
    "install",
    "dev",
    "lint",
    "format",
    "type-check",
    "test",
    "test-cov",
    "run",
    "migrate",
]


def _extract_targets() -> set[str]:
    """Parse the Makefile and extract all target names."""
    content = MAKEFILE_PATH.read_text(encoding="utf-8")
    targets: set[str] = set()
    # Match pattern: "target: ## comment" or "target:"
    for match in re.finditer(r"^([a-zA-Z0-9_-]+)\s*:", content, re.MULTILINE):
        targets.add(match.group(1))
    return targets


class TestMakefile:
    """Makefile must exist and contain all required targets."""

    def test_makefile_exists(self) -> None:
        """Makefile must exist at the project root."""
        assert MAKEFILE_PATH.is_file(), "Makefile is missing"

    def test_makefile_is_not_placeholder(self) -> None:
        """Makefile must have real content, not just a placeholder comment."""
        content = MAKEFILE_PATH.read_text(encoding="utf-8").strip()
        assert len(content) > 100, (
            f"Makefile is too short ({len(content)} chars). "
            "Expected full targets with implementations."
        )

    def test_all_required_targets_present(self) -> None:
        """Every target from the spec must be in the Makefile."""
        targets = _extract_targets()
        missing = [t for t in REQUIRED_TARGETS if t not in targets]
        assert not missing, (
            f"Missing Makefile targets: {missing}"
        )

    def test_help_is_default_target(self) -> None:
        """help should be the first/default target in the Makefile."""
        targets = _extract_targets()
        assert "help" in targets, "help target is missing"
        # help should be defined early (default target is the first one)
        content = MAKEFILE_PATH.read_text(encoding="utf-8")
        first_target_line = re.search(r"^([a-zA-Z0-9_-]+)\s*:", content, re.MULTILINE)
        assert first_target_line is not None, "No targets found in Makefile"
        assert first_target_line.group(1) == "help", (
            f"Expected 'help' as default target, got '{first_target_line.group(1)}'"
        )

    def test_makefile_has_phony_declaration(self) -> None:
        """Makefile should declare .PHONY to prevent conflicts with files."""
        content = MAKEFILE_PATH.read_text(encoding="utf-8")
        assert ".PHONY:" in content, (
            "Makefile is missing .PHONY declaration"
        )

    def test_makefile_targets_have_help_comments(self) -> None:
        """Each target should have a ## comment for make help output."""
        content = MAKEFILE_PATH.read_text(encoding="utf-8")
        targets = _extract_targets()
        help_targets: set[str] = set()
        for match in re.finditer(
            r"^([a-zA-Z0-9_-]+)\s*:.*##\s*(.+)$", content, re.MULTILINE
        ):
            help_targets.add(match.group(1))

        missing_help = targets - help_targets
        # .PHONY is not a real target with help
        missing_help.discard(".PHONY")
        assert not missing_help, (
            f"Targets missing help comments (##): {sorted(missing_help)}"
        )
