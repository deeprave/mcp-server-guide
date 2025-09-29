"""Tests to improve path validator coverage."""

import pytest
from unittest.mock import patch
from pathlib import Path
from src.mcp_server_guide.security.path_validator import PathValidator, SecurityError


def test_path_resolution_error():
    """Test path resolution error handling."""
    validator = PathValidator([Path("/allowed")])

    with patch("pathlib.Path.resolve") as mock_resolve:
        mock_resolve.side_effect = OSError("Permission denied")

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_path("some/path", Path("/base"))

        assert "Invalid path" in str(exc_info.value)


def test_path_value_error():
    """Test path value error handling."""
    validator = PathValidator([Path("/allowed")])

    with patch("pathlib.Path.resolve") as mock_resolve:
        mock_resolve.side_effect = ValueError("Invalid path format")

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_path("some/path", Path("/base"))

        assert "Invalid path" in str(exc_info.value)
