"""Tests for config_tools.py error handling scenarios."""

import pytest
from unittest.mock import patch, Mock

from mcp_server_guide.tools.config_tools import (
    set_project_config_values,
    set_project_config,
)
from mcp_server_guide.validation import ConfigValidationError


class TestConfigToolsErrorHandling:
    """Test error handling paths in config_tools.py."""

    @pytest.mark.asyncio
    async def test_set_project_config_values_validation_error(self):
        """Test ConfigValidationError handling in set_project_config_values."""
        # Mock validate_config to raise ConfigValidationError
        with patch("mcp_server_guide.tools.config_tools.validate_config") as mock_validate:
            mock_validate.side_effect = ConfigValidationError("Invalid config", ["error1", "error2"])

            result = await set_project_config_values({"invalid_key": "value"})

            assert result["success"] is False
            assert "Configuration validation failed" in result["error"]
            assert result["errors"] == ["error1", "error2"]

    @pytest.mark.asyncio
    async def test_set_project_config_validation_error(self):
        """Test ConfigValidationError handling in set_project_config."""
        # Mock the validation import inside the function
        with patch("mcp_server_guide.validation.validate_config_key") as mock_validate:
            mock_validate.side_effect = ConfigValidationError("Invalid key", ["error1"])

            result = await set_project_config("invalid_key", "value")

            assert result["success"] is False
            assert "Invalid key" in result["error"]
            assert result["errors"] == ["error1"]
            assert result["key"] == "invalid_key"
            assert result["value"] == "value"

    @pytest.mark.asyncio
    async def test_set_project_config_auto_save_exception(self):
        """Test exception handling in auto-save functionality."""
        # Mock the save_session import inside the function
        with patch("mcp_server_guide.tools.session_management.save_session") as mock_save:
            mock_save.side_effect = Exception("Save failed")

            # Mock logger to verify warning is logged
            with patch("mcp_server_guide.logging_config.get_logger") as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                # This should succeed despite save failure
                result = await set_project_config("docroot", "/test/path")

                assert result["success"] is True
                # Verify warning was logged
                mock_logger.warning.assert_called_once()
                assert "Failed to auto-save session" in mock_logger.warning.call_args[0][0]
