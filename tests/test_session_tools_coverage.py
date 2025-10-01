"""Tests to improve session_tools coverage."""

from unittest.mock import patch
from src.mcp_server_guide.session_tools import set_project_config
from src.mcp_server_guide.validation import ConfigValidationError


async def test_set_project_config_validation_error():
    """Test set_project_config with validation error."""
    with patch("src.mcp_server_guide.session_tools.validate_config_key") as mock_validate:
        mock_validate.side_effect = ConfigValidationError("Invalid key", errors=["test error"])

        result = set_project_config("invalid_key", "value")

        assert result["success"] is False
        assert "Invalid key" in result["error"]
        assert result["errors"] == ["test error"]
