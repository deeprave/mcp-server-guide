"""Tests to improve validation coverage."""

import pytest
from unittest.mock import patch
from src.mcp_server_guide.validation import validate_config_key, ConfigValidationError


def test_json_serialization_error():
    """Test that non-JSON-serializable values are rejected."""

    # Create a non-serializable object
    class NonSerializable:
        pass

    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config_key("custom_key", NonSerializable())

    assert "must be JSON serializable" in str(exc_info.value)


def test_schema_loading_error():
    """Test schema loading error handling."""
    with patch("src.mcp_server_guide.validation.resources.open_text") as mock_open_text:
        mock_open_text.side_effect = FileNotFoundError("Schema not found")

        with pytest.raises(ImportError) as exc_info:
            # Force reimport to trigger schema loading
            import importlib
            import src.mcp_server_guide.validation

            importlib.reload(src.mcp_server_guide.validation)

        assert "Failed to load config schema" in str(exc_info.value)
