"""Final coverage boost tests to reach 90% target."""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from mcp_server_guide.session import resolve_server_path
from mcp_server_guide.tools.session_management import cleanup_config, reset_session


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


@pytest.mark.asyncio
async def test_cleanup_config_directory_not_set():
    """Test cleanup_config when directory is not set - covers line 22."""
    # Mock the SessionManager to return a session where directory is not set
    mock_session = Mock()
    mock_session.is_directory_set.return_value = False

    with patch("mcp_server_guide.tools.session_management.SessionManager", return_value=mock_session):
        # The decorator should catch this and return the error before calling the actual function
        result = await cleanup_config()
        assert result["success"] is False
        assert "Working directory not set" in result["error"]
        assert result["blocked"] is True


async def test_reset_session_async_context():
    """Test reset_session in async context."""
    with patch("mcp_server_guide.tools.session_management.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session.set_current_project = AsyncMock()
        mock_session_class.return_value = mock_session

        with patch("mcp_server_guide.session_tools.reset_project_config", new_callable=AsyncMock) as mock_reset:
            with patch("os.path.basename", return_value="test_project"):
                result = await reset_session()
                assert result["success"] is True
                assert result["project"] == "test_project"
                # Verify async functions were awaited
                mock_session.set_current_project.assert_called_once_with("test_project")
                mock_reset.assert_called_once()
