"""Tests for HTTP security hardening."""

import pytest
import time
from unittest.mock import Mock, patch
import requests
from src.mcp_server_guide.http.secure_client import SecureHTTPClient, RateLimiter
from src.mcp_server_guide.exceptions import NetworkError, SecurityError


class TestRateLimiter:
    """Test rate limiting functionality."""

    def test_rate_limiter_allows_requests_within_limit(self):
        """Test that rate limiter allows requests within limit."""
        limiter = RateLimiter(max_requests=3, window_seconds=1)

        # Should allow 3 requests
        limiter.check_rate_limit()
        limiter.check_rate_limit()
        limiter.check_rate_limit()

    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test that rate limiter blocks requests over limit."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        # First 2 requests should pass
        limiter.check_rate_limit()
        limiter.check_rate_limit()

        # Third request should fail
        with pytest.raises(NetworkError, match="Rate limit exceeded"):
            limiter.check_rate_limit()

    def test_rate_limiter_resets_after_window(self):
        """Test that rate limiter resets after time window."""
        limiter = RateLimiter(max_requests=1, window_seconds=0.1)

        # First request should pass
        limiter.check_rate_limit()

        # Second request should fail
        with pytest.raises(NetworkError):
            limiter.check_rate_limit()

        # Wait for window to reset
        time.sleep(0.2)

        # Should allow request again
        limiter.check_rate_limit()


class TestSecureHTTPClient:
    """Test secure HTTP client functionality."""

    def test_client_initialization(self):
        """Test client initialization with default settings."""
        client = SecureHTTPClient()

        assert client.timeout == 30
        assert client.max_redirects == 3
        assert client.max_content_length == 10_000_000
        assert client.verify_ssl is True
        assert client.session is not None

    def test_client_custom_settings(self):
        """Test client initialization with custom settings."""
        client = SecureHTTPClient(timeout=60, max_redirects=5, max_content_length=5_000_000, verify_ssl=False)

        assert client.timeout == 60
        assert client.max_redirects == 5
        assert client.max_content_length == 5_000_000
        assert client.verify_ssl is False

    def test_url_validation_allows_valid_urls(self):
        """Test that valid URLs are allowed."""
        client = SecureHTTPClient()

        valid_urls = [
            "http://example.com",
            "https://example.com",
            "https://api.example.com/v1/data",
            "http://subdomain.example.org:8080/path",
        ]

        for url in valid_urls:
            # Should not raise exception
            client._validate_url(url)

    def test_url_validation_blocks_invalid_schemes(self):
        """Test that invalid URL schemes are blocked."""
        client = SecureHTTPClient()

        invalid_urls = [
            "ftp://example.com",
            "file:///etc/passwd",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
        ]

        for url in invalid_urls:
            with pytest.raises(SecurityError, match="Only HTTP/HTTPS URLs are allowed"):
                client._validate_url(url)

    def test_url_validation_blocks_localhost(self):
        """Test that localhost URLs are blocked."""
        client = SecureHTTPClient()

        localhost_urls = ["http://localhost:8080", "https://127.0.0.1:3000", "http://0.0.0.0:8000"]

        for url in localhost_urls:
            with pytest.raises(SecurityError, match="localhost"):
                client._validate_url(url)

    def test_url_validation_blocks_private_networks(self):
        """Test that private network URLs are blocked."""
        client = SecureHTTPClient()

        private_urls = ["http://192.168.1.1", "https://10.0.0.1", "http://172.16.0.1", "https://172.31.255.255"]

        for url in private_urls:
            with pytest.raises(SecurityError, match="private networks"):
                client._validate_url(url)

    def test_response_size_validation_allows_small_responses(self):
        """Test that small responses are allowed."""
        client = SecureHTTPClient(max_content_length=1000)

        mock_response = Mock()
        mock_response.headers = {"content-length": "500"}

        # Should not raise exception
        client._validate_response_size(mock_response)

    def test_response_size_validation_blocks_large_responses(self):
        """Test that large responses are blocked."""
        client = SecureHTTPClient(max_content_length=1000)

        mock_response = Mock()
        mock_response.headers = {"content-length": "2000"}

        with pytest.raises(NetworkError, match="Response too large"):
            client._validate_response_size(mock_response)

    def test_response_size_validation_allows_no_content_length(self):
        """Test that responses without content-length header are allowed."""
        client = SecureHTTPClient()

        mock_response = Mock()
        mock_response.headers = {}

        # Should not raise exception
        client._validate_response_size(mock_response)

    @patch("src.mcp_server_guide.http.secure_client.requests.Session")
    def test_get_request_success(self, mock_session_class):
        """Test successful GET request."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.headers = {"content-length": "100"}
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = SecureHTTPClient(rate_limit_requests=10)
        response = client.get("https://example.com")

        assert response == mock_response
        mock_session.get.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    @patch("src.mcp_server_guide.http.secure_client.requests.Session")
    def test_get_request_timeout_error(self, mock_session_class):
        """Test GET request timeout handling."""
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.Timeout("Timeout")
        mock_session_class.return_value = mock_session

        client = SecureHTTPClient()

        with pytest.raises(NetworkError, match="Request timeout"):
            client.get("https://example.com")

    @patch("src.mcp_server_guide.http.secure_client.requests.Session")
    def test_get_request_connection_error(self, mock_session_class):
        """Test GET request connection error handling."""
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        mock_session_class.return_value = mock_session

        client = SecureHTTPClient()

        with pytest.raises(NetworkError, match="Connection error"):
            client.get("https://example.com")

    @patch("src.mcp_server_guide.http.secure_client.requests.Session")
    def test_get_request_http_error(self, mock_session_class):
        """Test GET request HTTP error handling."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}
        http_error = requests.exceptions.HTTPError("404 Not Found")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = SecureHTTPClient()

        with pytest.raises(NetworkError, match="HTTP error 404"):
            client.get("https://example.com")

    def test_get_request_rate_limit_enforcement(self):
        """Test that rate limiting is enforced on GET requests."""
        client = SecureHTTPClient(rate_limit_requests=1, rate_limit_window=1)

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.headers = {}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # First request should succeed
            client.get("https://example.com")

            # Second request should fail due to rate limit
            with pytest.raises(NetworkError, match="Rate limit exceeded"):
                client.get("https://example.com")

    def test_get_request_url_validation(self):
        """Test that URL validation is enforced on GET requests."""
        client = SecureHTTPClient()

        with pytest.raises(SecurityError):
            client.get("http://localhost:8080")

    @patch("src.mcp_server_guide.http.secure_client.requests.Session")
    def test_post_request_success(self, mock_session_class):
        """Test successful POST request."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.headers = {"content-length": "100"}
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = SecureHTTPClient(rate_limit_requests=10)
        response = client.post("https://example.com", json={"data": "test"})

        assert response == mock_response
        mock_session.post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    def test_context_manager(self):
        """Test client as context manager."""
        with SecureHTTPClient() as client:
            assert client.session is not None

        # Session should be closed after context exit
        # Note: We can't easily test this without mocking, but the structure is correct

    def test_session_security_headers(self):
        """Test that session has secure headers."""
        client = SecureHTTPClient()

        headers = client.session.headers
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Accept-Encoding" in headers
        assert "Connection" in headers

    def test_ssl_verification_enabled_by_default(self):
        """Test that SSL verification is enabled by default."""
        client = SecureHTTPClient()
        assert client.session.verify is True

    def test_ssl_verification_can_be_disabled(self):
        """Test that SSL verification can be disabled."""
        client = SecureHTTPClient(verify_ssl=False)
        assert client.session.verify is False


class TestHTTPSecurityIntegration:
    """Test HTTP security integration scenarios."""

    def test_multiple_requests_with_rate_limiting(self):
        """Test multiple requests with rate limiting."""
        client = SecureHTTPClient(rate_limit_requests=2, rate_limit_window=0.1)

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.headers = {}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # First two requests should succeed
            client.get("https://example.com")
            client.get("https://example.com")

            # Third request should fail
            with pytest.raises(NetworkError, match="Rate limit exceeded"):
                client.get("https://example.com")

            # Wait for rate limit to reset
            time.sleep(0.2)

            # Should work again
            client.get("https://example.com")

    def test_security_error_context_preservation(self):
        """Test that security errors preserve context."""
        client = SecureHTTPClient()

        try:
            client.get("http://localhost:8080/api")
            assert False, "Should have raised SecurityError"
        except SecurityError as e:
            assert "localhost" in str(e)
            assert e.error_code == "SecurityError"
