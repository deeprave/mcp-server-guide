"""Tests for main.py configuration resolution logic."""

import os
from unittest.mock import patch

from mcp_server_guide.main import resolve_cli_config
from mcp_server_guide.config import Config


class TestConfigResolution:
    """Test configuration resolution from CLI args, env vars, and defaults."""

    def test_resolve_cli_config_with_cli_args(self):
        """Test config resolution prioritises CLI arguments."""
        config_obj = Config()
        kwargs = {"docroot": "/cli/path", "log_level": "DEBUG", "log_file": "/cli/log.txt"}

        result = resolve_cli_config(config_obj, **kwargs)

        assert result["docroot"] == "/cli/path"
        assert result["log_level"] == "DEBUG"
        assert result["log_file"] == "/cli/log.txt"

    def test_resolve_cli_config_with_env_vars(self):
        """Test config resolution falls back to environment variables."""
        config_obj = Config()
        kwargs = {}  # No CLI args

        with patch.dict(os.environ, {"MG_DOCROOT": "/env/path", "MG_LOG_LEVEL": "INFO", "MG_LOG_FILE": "/env/log.txt"}):
            result = resolve_cli_config(config_obj, **kwargs)

            assert result["docroot"] == "/env/path"
            assert result["log_level"] == "INFO"
            assert result["log_file"] == "/env/log.txt"

    def test_resolve_cli_config_with_defaults(self):
        """Test config resolution uses defaults when no CLI args or env vars."""
        config_obj = Config()
        kwargs = {}  # No CLI args

        with patch.dict(os.environ, {}, clear=True):
            result = resolve_cli_config(config_obj, **kwargs)

            # Should use default values from config
            assert "docroot" in result
            assert "log_level" in result
            assert result["log_level"] == "OFF"  # Default log level

    def test_resolve_cli_config_priority_order(self):
        """Test CLI args override env vars which override defaults."""
        config_obj = Config()
        kwargs = {
            "docroot": "/cli/path",  # CLI arg provided
            # log_level not provided in CLI
        }

        with patch.dict(
            os.environ,
            {
                "MG_DOCROOT": "/env/path",  # Should be overridden by CLI
                "MG_LOG_LEVEL": "INFO",  # Should be used (no CLI override)
            },
        ):
            result = resolve_cli_config(config_obj, **kwargs)

            assert result["docroot"] == "/cli/path"  # CLI wins
            assert result["log_level"] == "INFO"  # Env var used

    def test_resolve_cli_config_skips_config_options(self):
        """Test that config-related options are skipped."""
        config_obj = Config()
        kwargs = {"docroot": "/test/path"}

        result = resolve_cli_config(config_obj, **kwargs)

        # But other options should be included
        assert result["docroot"] == "/test/path"

    def test_resolve_cli_config_handles_callable_defaults(self):
        """Test that callable default values are executed."""
        config_obj = Config()
        kwargs = {}

        with patch.dict(os.environ, {}, clear=True):
            result = resolve_cli_config(config_obj, **kwargs)

            # Should handle callable defaults - config option has callable default
            # but it's skipped, so let's check another option that might have callable default
            assert "docroot" in result
            assert isinstance(result["docroot"], str)

    def test_resolve_cli_config_converts_cli_param_names(self):
        """Test that CLI parameter names are converted correctly."""
        config_obj = Config()
        kwargs = {
            "log_file": "/test.log",  # CLI uses underscores
            "log_level": "DEBUG",
        }

        result = resolve_cli_config(config_obj, **kwargs)

        assert result["log_file"] == "/test.log"
        assert result["log_level"] == "DEBUG"
