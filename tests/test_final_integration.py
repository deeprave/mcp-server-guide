"""Final coverage boost tests to reach 90% target."""

from mcp_server_guide.session import resolve_server_path


def test_resolve_server_path_absolute():
    """Test resolve_server_path with absolute path."""
    result = resolve_server_path("/absolute/path", "test_context")
    assert result == "/absolute/path"


def test_resolve_server_path_file_url():
    """Test resolve_server_path with file:// URL."""
    result = resolve_server_path("file:///absolute/path", "test_context")
    assert result == "/absolute/path"


def test_resolve_server_path_relative_file_url():
    """Test resolve_server_path with relative file:// URL."""
    result = resolve_server_path("file://relative/path", "test_context")
    # This should resolve to current directory + relative/path
    assert "relative/path" in result
