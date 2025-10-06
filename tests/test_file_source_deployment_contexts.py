"""Tests for file source deployment context detection and edge cases."""

import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from mcp_server_guide.file_source import FileSource, FileSourceType, FileAccessor


class TestDeploymentContextDetection:
    """Test deployment context detection functionality."""

    def test_detect_deployment_context_server_mode_set(self):
        """Test that SERVER_MODE environment variable triggers server context."""
        with patch.dict(os.environ, {"SERVER_MODE": "true"}):
            context = FileSource.detect_deployment_context()
            assert context == FileSourceType.SERVER

    def test_detect_deployment_context_docker_container_set(self):
        """Test that DOCKER_CONTAINER environment variable triggers server context."""
        with patch.dict(os.environ, {"DOCKER_CONTAINER": "true"}):
            context = FileSource.detect_deployment_context()
            assert context == FileSourceType.SERVER

    def test_detect_deployment_context_both_variables_set(self):
        """Test that both environment variables still trigger server context."""
        with patch.dict(os.environ, {"SERVER_MODE": "1", "DOCKER_CONTAINER": "1"}):
            context = FileSource.detect_deployment_context()
            assert context == FileSourceType.SERVER

    def test_detect_deployment_context_no_variables_defaults_local(self):
        """Test that no environment variables defaults to local context."""
        with patch.dict(os.environ, {}, clear=True):
            context = FileSource.detect_deployment_context()
            assert context == FileSourceType.LOCAL

    def test_detect_deployment_context_malformed_server_mode(self):
        """Test that any non-empty SERVER_MODE value triggers server context."""
        # Non-empty values trigger server context (current behavior)
        for value in ["unexpected", "foobar", "123"]:
            with patch.dict(os.environ, {"SERVER_MODE": value}, clear=True):
                context = FileSource.detect_deployment_context()
                assert context == FileSourceType.SERVER

        # Empty string should default to LOCAL (falsy value)
        with patch.dict(os.environ, {"SERVER_MODE": ""}, clear=True):
            context = FileSource.detect_deployment_context()
            assert context == FileSourceType.LOCAL

    def test_get_context_default_uses_detected_context(self):
        """Test that get_context_default uses detected deployment context."""
        with patch.dict(os.environ, {"SERVER_MODE": "true"}):
            source = FileSource.get_context_default("/test/path")
            assert source.type == FileSourceType.SERVER
            assert source.base_path == "/test/path"


class TestSessionPathParsing:
    """Test session path parsing edge cases."""

    def test_from_session_path_client_double_slash_prefix(self):
        """Test client:// prefix handling."""
        source = FileSource.from_session_path("client://test/path", "project")
        assert source.type == FileSourceType.LOCAL
        assert source.base_path == "test/path"

    def test_from_session_path_server_double_slash_prefix(self):
        """Test server:// prefix handling."""
        source = FileSource.from_session_path("server://test/path", "project")
        assert source.type == FileSourceType.SERVER
        assert source.base_path == "test/path"

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
    """Test file URL processing edge cases."""

    def test_from_file_url_with_leading_slash_removal(self):
        """Test file:// URL processing removes extra leading slash."""
        with patch.object(FileSource, "detect_deployment_context", return_value=FileSourceType.LOCAL):
            source = FileSource._from_file_url("file://relative/path")
            assert source.base_path == "relative/path"

    def test_from_file_url_file_prefix_only(self):
        """Test file: prefix handling."""
        with patch.object(FileSource, "detect_deployment_context", return_value=FileSourceType.LOCAL):
            source = FileSource._from_file_url("file:test/path")
            assert source.base_path == "test/path"

    def test_from_file_url_uses_server_context_when_detected(self):
        """Test file URL uses server context when environment indicates server."""
        with patch.dict(os.environ, {"SERVER_MODE": "true"}):
            source = FileSource._from_file_url("file:///absolute/path")
            assert source.type == FileSourceType.SERVER
            assert source.base_path == "/absolute/path"


class TestHttpFileReading:
    """Test HTTP file reading edge cases."""

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


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple features."""

    def test_server_deployment_file_url_integration(self):
        """Test file URL processing in server deployment context."""
        with patch.dict(os.environ, {"DOCKER_CONTAINER": "true"}):
            source = FileSource.from_url("file:///app/config.json")
            assert source.type == FileSourceType.SERVER
            assert source.base_path == "/app/config.json"

    def test_local_development_context_default(self):
        """Test local development context with default path."""
        with patch.dict(os.environ, {}, clear=True):
            source = FileSource.get_context_default("config.json")
            assert source.type == FileSourceType.LOCAL
            assert source.base_path == "config.json"
