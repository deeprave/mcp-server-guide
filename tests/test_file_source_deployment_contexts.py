"""Tests for file source path handling and HTTP edge cases."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server_guide.file_source import FileAccessor, FileSource, FileSourceType


class TestSessionPathParsing:
    """Test session path parsing for different URL types."""

    def test_from_session_path_regular_path(self):
        """Test regular file path handling."""
        source = FileSource.from_session_path("test/path", "project")
        assert source.type == FileSourceType.FILE
        assert source.base_path == "test/path"

    def test_from_session_path_nested_path(self):
        """Test nested file path handling."""
        source = FileSource.from_session_path("server/test/path", "project")
        assert source.type == FileSourceType.FILE
        assert source.base_path == "server/test/path"

    def test_from_session_path_http_url(self):
        """Test HTTP URL handling in session paths."""
        source = FileSource.from_session_path("https://example.com/path", "project")
        assert source.type == FileSourceType.HTTP
        assert source.base_path == "https://example.com/path"

    def test_from_session_path_http_url_no_ssl(self):
        """Test HTTP URL handling without SSL."""
        source = FileSource.from_session_path("http://example.com/path", "project")
        assert source.type == FileSourceType.HTTP
        assert source.base_path == "http://example.com/path"


class TestFileUrlProcessing:
    """Test file:// URL processing edge cases."""

    def test_from_file_url_absolute_path(self):
        """Test file:// URL with absolute path."""
        source = FileSource._from_file_url("file:///absolute/path")
        assert source.type == FileSourceType.FILE
        assert source.base_path == "/absolute/path"

    def test_from_file_url_relative_path(self):
        """Test file:// URL with relative path."""
        source = FileSource._from_file_url("file://relative/path")
        assert source.type == FileSourceType.FILE
        assert source.base_path == "relative/path"

    def test_from_file_url_file_prefix_only(self):
        """Test file: prefix handling."""
        source = FileSource._from_file_url("file:test/path")
        assert source.type == FileSourceType.FILE
        assert source.base_path == "test/path"


class TestHttpFileReading:
    """Test HTTP file reading with caching."""

    @pytest.mark.asyncio
    async def test_read_http_file_cache_update_for_fresh_request(self):
        """Test cache update for fresh HTTP requests."""
        source = FileSource(FileSourceType.HTTP, "https://example.com")
        accessor = FileAccessor()

        # No cached entry
        accessor.cache = MagicMock()
        accessor.cache.get.return_value = None

        # Mock HTTP client
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "fresh content"
        mock_response.headers = {"etag": "xyz789"}
        mock_client.get.return_value = mock_response

        with patch("mcp_server_guide.http.async_client.AsyncHTTPClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await accessor._read_http_file("test.txt", source)

            assert result == "fresh content"
            accessor.cache.put.assert_called_once_with(
                "https://example.com/test.txt", "fresh content", headers={"etag": "xyz789"}
            )

    @pytest.mark.asyncio
    async def test_read_http_file_runtime_error_on_failure(self):
        """Test RuntimeError raised when HTTP request fails with no cache."""
        source = FileSource(FileSourceType.HTTP, "https://example.com")
        accessor = FileAccessor()

        # No cached entry
        accessor.cache = MagicMock()
        accessor.cache.get.return_value = None

        # Mock HTTP client that raises exception
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Network error")

        with patch("mcp_server_guide.http.async_client.AsyncHTTPClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with pytest.raises(RuntimeError, match="Failed to read HTTP file"):
                await accessor._read_http_file("test.txt", source)


class TestContextDefaults:
    """Test default file source context behaviour."""

    def test_get_context_default_creates_file_source(self):
        """Test that get_context_default always creates FILE type source.

        All file sources are relative to the server's working directory.
        There is no client-side path support.
        """
        source = FileSource.get_context_default("test/path")
        assert source.type == FileSourceType.FILE
        assert source.base_path == "test/path"

    def test_get_context_default_with_absolute_path(self):
        """Test get_context_default with absolute path."""
        source = FileSource.get_context_default("/app/config.yaml")
        assert source.type == FileSourceType.FILE
        assert source.base_path == "/app/config.yaml"
