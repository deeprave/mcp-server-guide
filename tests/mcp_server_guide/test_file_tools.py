"""Tests for file tools functionality."""

from unittest.mock import AsyncMock, patch

from mcp_server_guide.tools.file_tools import get_file_content


async def test_get_file_content_error_handling():
    """Test get_file_content with various error conditions."""
    # Test with non-existent file
    with patch("pathlib.Path.exists", return_value=False):
        result = await get_file_content("nonexistent.txt")
        assert "File not found" in result

    # Test with path that exists but is not a file
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=False):
            result = await get_file_content("directory")
            assert "File not found" in result

    # Test with read error
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("aiofiles.open", side_effect=Exception("Permission denied")):
                result = await get_file_content("error.txt")
                assert "Error reading file" in result

    # Test successful read
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_file", return_value=True):
            # Mock aiofiles.open context manager properly
            mock_file = AsyncMock()
            mock_file.read = AsyncMock(return_value="file content")
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_file)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            with patch("aiofiles.open", return_value=mock_context):
                result = await get_file_content("test.txt")
                assert result == "file content"
