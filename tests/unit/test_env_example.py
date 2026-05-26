"""Tests for .env.example template (T02 verification).

Validates that .env.example exists and contains all required environment
variables with placeholder values (no real secrets).
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"

# Required variables from docs/SECURITY.md and tasks/plan.md Task 4
REQUIRED_VARIABLES = [
    "DATABASE_URL",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "MAX_BATCH_SIZE",
    "MAX_FILE_SIZE_MB",
    "RATE_LIMIT_PER_MINUTE",
    "DEBUG",
    "HOST",
    "PORT",
]

# Patterns that indicate a real secret (not a placeholder)
# These would fail the "no real secrets" check
LIVE_SECRET_PATTERNS = [
    # Looks like a real hex key (32+ chars of hex)
    r"SECRET_KEY\s*=\s*[a-f0-9]{64,}",
    # Looks like a real bcrypt hash
    r"\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}",
    # Real-looking passwords that are not the documented placeholders
    r"PASSWORD\s*=\s*(?!.*(change.me|your_|postgres:postgres))",
]


def _parse_env_vars() -> dict[str, str]:
    """Parse .env.example into a dict of VAR=value."""
    content = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


class TestEnvExample:
    """.env.example must exist, use placeholders, and list all required vars."""

    def test_env_example_exists(self) -> None:
        """.env.example must exist at the project root."""
        assert ENV_EXAMPLE_PATH.is_file(), ".env.example is missing"

    def test_env_example_not_empty(self) -> None:
        """.env.example must not be empty (was a placeholder file before)."""
        content = ENV_EXAMPLE_PATH.read_text(encoding="utf-8").strip()
        assert len(content) > 50, (
            f".env.example is too short ({len(content)} chars). "
            "Expected a full template with all variables."
        )

    def test_all_required_variables_present(self) -> None:
        """All required environment variables must be listed."""
        env_vars = _parse_env_vars()
        missing = [v for v in REQUIRED_VARIABLES if v not in env_vars]
        assert not missing, (
            f"Missing required variables in .env.example: {missing}"
        )

    def test_no_real_secrets_in_env_example(self) -> None:
        """.env.example must use placeholders, not real secrets."""
        content = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
        for pattern in LIVE_SECRET_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            assert match is None, (
                f"Possible real secret found in .env.example: "
                f"pattern '{pattern}' matched near character {match.start() if match else -1}"
            )

    def test_secret_key_is_placeholder(self) -> None:
        """SECRET_KEY must be a placeholder, not a real key."""
        env_vars = _parse_env_vars()
        secret_key = env_vars.get("SECRET_KEY", "")
        placeholder_markers = ["change-me", "change_me", "your_", "placeholder", "<"]
        is_placeholder = any(marker in secret_key.lower() for marker in placeholder_markers)
        # Also consider short values as placeholders (real keys should be long)
        is_short = len(secret_key) < 40
        assert is_placeholder or is_short, (
            f"SECRET_KEY looks like a real value: '{secret_key[:20]}...'"
        )

    def test_database_url_is_placeholder(self) -> None:
        """DATABASE_URL must use placeholder credentials."""
        env_vars = _parse_env_vars()
        db_url = env_vars.get("DATABASE_URL", "")
        assert "change-me" in db_url.lower() or "your_" in db_url.lower() or "localhost" in db_url, (
            f"DATABASE_URL looks like it contains real credentials: {db_url}"
        )

    def test_debug_is_false(self) -> None:
        """DEBUG must default to false for safety."""
        env_vars = _parse_env_vars()
        debug_val = env_vars.get("DEBUG", "").lower()
        assert debug_val in ("false", "0", "no"), (
            f"DEBUG should be false, got {debug_val!r}"
        )

    def test_variables_have_comments(self) -> None:
        """.env.example should have comments explaining each variable."""
        content = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
        comment_lines = [ln for ln in content.splitlines() if ln.strip().startswith("#")]
        assert len(comment_lines) >= 5, (
            f".env.example has only {len(comment_lines)} comment lines. "
            "Expected descriptive comments for variables."
        )
