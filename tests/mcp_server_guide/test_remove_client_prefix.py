"""Test removal of client:// prefix support."""

import pytest

from mcp_server_guide.file_source import FileSource


def test_client_prefix_unsupported():
    """Test that client:// prefix raises an error."""
    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        FileSource.from_url("client://some/path")


def test_client_double_slash_prefix_unsupported():
    """Test that client:// prefix raises an error."""
    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        FileSource.from_url("client://some/path")
