"""Tests for SecureHTTPClient missing coverage."""

import pytest
from unittest.mock import Mock, patch
import requests
from mcp_server_guide.http.secure_client import SecureHTTPClient, get_default_client, RateLimiter
from mcp_server_guide.exceptions import SecurityError, NetworkError


class TestSecureHTTPClient:
    """Test SecureHTTPClient missing coverage."""

    def test_validate_url_no_hostname(self):
        """Test URL validation with no hostname (line 108)."""
        client = SecureHTTPClient()
        with pytest.raises(SecurityError, match="Invalid URL: no hostname"):
            client._validate_url("http://")

    def test_validate_url_private_network_172_2x(self):
        """Test URL validation blocks 172.2x networks (line 126)."""
        client = SecureHTTPClient()
        with pytest.raises(SecurityError, match="Requests to private networks are not allowed"):
            client._validate_url("http://172.20.1.1")

    def test_validate_response_size_too_large(self):
        """Test response size validation when too large (line 180)."""
        client = SecureHTTPClient(max_content_length=1000)
        mock_response = Mock()
        mock_response.headers = {"content-length": "2000"}

        with pytest.raises(NetworkError, match="Response too large"):
            client._validate_response_size(mock_response)

    def test_post_timeout_error(self):
        """Test POST request timeout error (line 203)."""
        with patch("requests.Session.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout()
            client = SecureHTTPClient()

            with pytest.raises(NetworkError, match="Request timeout"):
                client.post("http://example.com")

    def test_post_connection_error(self):
        """Test POST request connection error (line 205)."""
        with patch("requests.Session.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError()
            client = SecureHTTPClient()

            with pytest.raises(NetworkError, match="Connection error"):
                client.post("http://example.com")

    def test_post_http_error(self):
        """Test POST request HTTP error (line 207)."""
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 404
            http_error = requests.exceptions.HTTPError()
            http_error.response = mock_response
            mock_post.side_effect = http_error
            client = SecureHTTPClient()

            with pytest.raises(NetworkError, match="HTTP error 404"):
                client.post("http://example.com")

    def test_post_request_exception(self):
        """Test POST request general exception (line 209)."""
        with patch("requests.Session.post") as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException()
            client = SecureHTTPClient()

            with pytest.raises(NetworkError, match="Request failed"):
                client.post("http://example.com")

    def test_close_with_session(self):
        """Test close method when session exists (line 231)."""
        client = SecureHTTPClient()
        mock_session = Mock()
        client.session = mock_session

        client.close()
        mock_session.close.assert_called_once()

    def test_close_without_session(self):
        """Test close method when session is None (line 233)."""
        client = SecureHTTPClient()
        client.session = None

        # Should not raise an error
        client.close()

    def test_get_default_client_creates_new(self):
        """Test get_default_client creates new client when none exists."""
        # Reset global client
        import mcp_server_guide.http.secure_client as module

        module._default_client = None

        client = get_default_client()
        assert isinstance(client, SecureHTTPClient)
        assert module._default_client is client

    def test_get_default_client_returns_existing(self):
        """Test get_default_client returns existing client."""
        # Set up existing client
        import mcp_server_guide.http.secure_client as module

        existing_client = SecureHTTPClient()
        module._default_client = existing_client

        client = get_default_client()
        assert client is existing_client


class TestRateLimiter:
    """Test RateLimiter missing coverage."""

    def test_rate_limiter_window_cleanup(self):
        """Test rate limiter cleans up old requests."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        # Add old request (should be cleaned up)
        limiter.requests = [0.0]  # Very old timestamp

        # This should not raise because old request is cleaned up
        limiter.check_rate_limit()
        limiter.check_rate_limit()

        # This should raise because we're at the limit
        with pytest.raises(NetworkError, match="Rate limit exceeded"):
            limiter.check_rate_limit()
