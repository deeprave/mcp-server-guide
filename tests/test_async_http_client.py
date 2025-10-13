"""Tests for AsyncHTTPClient."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import aiohttp

from mcp_server_guide.http.async_client import AsyncHTTPClient


class TestAsyncHTTPClient:
    """Test AsyncHTTPClient functionality."""

    def test_init(self):
        """Test client initialization."""
        client = AsyncHTTPClient(timeout=60, max_redirects=10)
        assert client.timeout.total == 60
        assert client.max_redirects == 10
        assert client._session is None

    def test_init_defaults(self):
        """Test client initialization with defaults."""
        client = AsyncHTTPClient()
        assert client.timeout.total == 30
        assert client.max_redirects == 5
        assert client._session is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = Mock()
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session

            async with AsyncHTTPClient() as client:
                assert client._session == mock_session
                mock_session_class.assert_called_once()

            mock_session.close.assert_called_once()

    def test_validate_url_valid_http(self):
        """Test URL validation with valid HTTP URL."""
        client = AsyncHTTPClient()
        # Should not raise
        client._validate_url("http://example.com/path")

    def test_validate_url_valid_https(self):
        """Test URL validation with valid HTTPS URL."""
        client = AsyncHTTPClient()
        # Should not raise
        client._validate_url("https://example.com/path")

    def test_validate_url_invalid_scheme(self):
        """Test URL validation with invalid scheme."""
        client = AsyncHTTPClient()
        with pytest.raises(ValueError, match="Invalid URL scheme: ftp"):
            client._validate_url("ftp://example.com")

    def test_validate_url_no_scheme(self):
        """Test URL validation with no scheme."""
        client = AsyncHTTPClient()
        with pytest.raises(ValueError, match="Invalid URL scheme: "):
            client._validate_url("example.com")

    def test_validate_url_no_netloc(self):
        """Test URL validation with no netloc."""
        client = AsyncHTTPClient()
        with pytest.raises(ValueError, match="URL must have a valid hostname"):
            client._validate_url("http://")

    def test_validate_url_localhost_blocked(self):
        """Test URL validation blocks localhost."""
        client = AsyncHTTPClient()
        with pytest.raises(ValueError, match="Access to localhost is not allowed"):
            client._validate_url("http://localhost/path")

    def test_validate_url_127_0_0_1_blocked(self):
        """Test URL validation blocks 127.0.0.1."""
        client = AsyncHTTPClient()
        with pytest.raises(ValueError, match="Access to localhost is not allowed"):
            client._validate_url("http://127.0.0.1/path")

    def test_validate_url_ipv6_localhost_blocked(self):
        """Test URL validation blocks IPv6 localhost."""
        client = AsyncHTTPClient()
        with pytest.raises(ValueError, match="Access to localhost is not allowed"):
            client._validate_url("http://[::1]/path")

    @pytest.mark.asyncio
    async def test_get_no_session(self):
        """Test GET request without initialized session."""
        client = AsyncHTTPClient()
        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client.get("http://example.com")

    @pytest.mark.asyncio
    async def test_get_success(self):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = AsyncMock(return_value="response content")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_response)
        mock_session.close = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                result = await client.get("http://example.com")

                assert result == "response content"
                mock_session.get.assert_called_once_with("http://example.com", headers=None)
                mock_response.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_with_headers(self):
        """Test GET request with custom headers."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = AsyncMock(return_value="response content")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_response)
        mock_session.close = AsyncMock()

        headers = {"Authorization": "Bearer token"}

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                result = await client.get("http://example.com", headers=headers)

                assert result == "response content"
                mock_session.get.assert_called_once_with("http://example.com", headers=headers)

    @pytest.mark.asyncio
    async def test_get_client_error(self):
        """Test GET request with client error."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock(
            side_effect=aiohttp.ClientResponseError(request_info=Mock(), history=(), status=404)
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = Mock()
        mock_session.get = Mock(return_value=mock_response)
        mock_session.close = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                with pytest.raises(aiohttp.ClientResponseError):
                    await client.get("http://example.com")

    @pytest.mark.asyncio
    async def test_get_timeout_error(self):
        """Test GET request with timeout error."""
        mock_session = Mock()
        mock_session.get = Mock(side_effect=asyncio.TimeoutError())
        mock_session.close = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                with pytest.raises(asyncio.TimeoutError):
                    await client.get("http://example.com")

    @pytest.mark.asyncio
    async def test_get_invalid_url(self):
        """Test GET request with invalid URL."""
        mock_session = Mock()
        mock_session.close = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                with pytest.raises(ValueError, match="Invalid URL scheme"):
                    await client.get("ftp://example.com")

    @pytest.mark.asyncio
    async def test_post_no_session(self):
        """Test POST request without initialized session."""
        client = AsyncHTTPClient()
        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client.post("http://example.com")

    @pytest.mark.asyncio
    async def test_post_success(self):
        """Test successful POST request."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = AsyncMock(return_value="response content")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_response)
        mock_session.close = AsyncMock()

        data = {"key": "value"}

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                result = await client.post("http://example.com", data=data)

                assert result == "response content"
                mock_session.post.assert_called_once_with("http://example.com", json=data, headers=None)
                mock_response.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_with_headers(self):
        """Test POST request with custom headers."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = AsyncMock(return_value="response content")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_response)
        mock_session.close = AsyncMock()

        data = {"key": "value"}
        headers = {"Content-Type": "application/json"}

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                result = await client.post("http://example.com", data=data, headers=headers)

                assert result == "response content"
                mock_session.post.assert_called_once_with("http://example.com", json=data, headers=headers)

    @pytest.mark.asyncio
    async def test_post_client_error(self):
        """Test POST request with client error."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock(
            side_effect=aiohttp.ClientResponseError(request_info=Mock(), history=(), status=400)
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = Mock()
        mock_session.post = Mock(return_value=mock_response)
        mock_session.close = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                with pytest.raises(aiohttp.ClientResponseError):
                    await client.post("http://example.com")

    @pytest.mark.asyncio
    async def test_post_timeout_error(self):
        """Test POST request with timeout error."""
        mock_session = Mock()
        mock_session.post = Mock(side_effect=asyncio.TimeoutError())
        mock_session.close = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                with pytest.raises(asyncio.TimeoutError):
                    await client.post("http://example.com")

    @pytest.mark.asyncio
    async def test_post_invalid_url(self):
        """Test POST request with invalid URL."""
        mock_session = Mock()
        mock_session.close = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            async with AsyncHTTPClient() as client:
                with pytest.raises(ValueError, match="Invalid URL scheme"):
                    await client.post("ftp://example.com")
