"""Tests for app/config.py Settings class (T04 verification).

Validates that Settings can be imported, has all required fields with correct
defaults, and supports environment variable overrides.
"""

from __future__ import annotations

import pytest


class TestSettingsImports:
    """Settings class must be importable from app.config."""

    def test_config_module_imports(self) -> None:
        """app.config module should be importable without errors."""
        from app import config  # noqa: F401

        assert config is not None

    def test_settings_class_exists(self) -> None:
        """Settings class must exist in app.config."""
        from app.config import Settings

        assert Settings is not None


class TestSettingsDefaults:
    """Settings must have correct default values when environment is clean."""

    @pytest.fixture(autouse=True)
    def _clean_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Remove any env vars that might interfere with default tests."""
        env_vars = [
            "DATABASE_URL",
            "SYNC_DATABASE_URL",
            "SECRET_KEY",
            "ALGORITHM",
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "MAX_BATCH_SIZE",
            "MAX_FILE_SIZE_MB",
            "RATE_LIMIT_PER_MINUTE",
            "CORS_ORIGINS",
            "DEBUG",
            "HOST",
            "PORT",
        ]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

    def test_database_url_default_is_async(self) -> None:
        """DATABASE_URL should default to an async postgresql+asyncpg URL."""
        from app.config import Settings

        settings = Settings()
        assert isinstance(settings.DATABASE_URL, str)
        assert "postgresql" in settings.DATABASE_URL

    def test_algorithm_default_is_hs256(self) -> None:
        """ALGORITHM should default to HS256."""
        from app.config import Settings

        settings = Settings()
        assert settings.ALGORITHM == "HS256"

    def test_access_token_expire_minutes_default_is_30(self) -> None:
        """ACCESS_TOKEN_EXPIRE_MINUTES should default to 30."""
        from app.config import Settings

        settings = Settings()
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_debug_default_is_false(self) -> None:
        """DEBUG should default to False (secure default)."""
        from app.config import Settings

        settings = Settings()
        assert settings.DEBUG is False

    def test_max_batch_size_default_is_1000(self) -> None:
        """MAX_BATCH_SIZE should default to 1000."""
        from app.config import Settings

        settings = Settings()
        assert settings.MAX_BATCH_SIZE == 1000

    def test_rate_limit_default_is_100(self) -> None:
        """RATE_LIMIT_PER_MINUTE should default to 100."""
        from app.config import Settings

        settings = Settings()
        assert settings.RATE_LIMIT_PER_MINUTE == 100


class TestSettingsOverrides:
    """Settings must respect environment variable overrides."""

    def test_env_var_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Setting an env var should override the default value."""
        monkeypatch.setenv("ALGORITHM", "RS256")
        monkeypatch.setenv("SECRET_KEY", "test-secret-override")
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
        monkeypatch.setenv("SYNC_DATABASE_URL", "postgresql://test:test@localhost/test")

        from app.config import Settings

        settings = Settings()
        assert settings.ALGORITHM == "RS256"
        assert settings.SECRET_KEY == "test-secret-override"
        assert "test:test" in settings.DATABASE_URL
        assert "test:test" in settings.SYNC_DATABASE_URL
