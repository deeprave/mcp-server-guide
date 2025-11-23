"""Secure HTTP client with security hardening."""

import time
from typing import Any, List, Optional
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..exceptions import NetworkError, SecurityError


class RateLimiter:
    """Simple rate limiter for HTTP requests."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []

    def check_rate_limit(self) -> None:
        """Check if request is within rate limit."""
        now = time.time()
        # Remove old requests outside the window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.window_seconds]

        if len(self.requests) >= self.max_requests:
            raise NetworkError(
                f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds} seconds",
                error_code="RATE_LIMIT_EXCEEDED",
            )

        self.requests.append(now)


class SecureHTTPClient:
    """HTTP client with security hardening features."""

    def __init__(
        self,
        timeout: int = 30,
        max_redirects: int = 3,
        max_content_length: int = 10_000_000,  # 10MB
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
        verify_ssl: bool = True,
    ):
        """Initialize secure HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_redirects: Maximum number of redirects to follow
            max_content_length: Maximum response content length in bytes
            rate_limit_requests: Maximum requests per window
            rate_limit_window: Rate limit window in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.max_content_length = max_content_length
        self.verify_ssl = verify_ssl
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window)
        self.session = self._create_secure_session()

    def _create_secure_session(self) -> requests.Session:
        """Create a secure requests session."""
        session = requests.Session()
        session.verify = self.verify_ssl

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set secure headers
        session.headers.update(
            {
                "User-Agent": "MCP-Server-Guide/1.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

        return session

    def _validate_url(self, url: str) -> None:
        """Validate URL for security issues.

        Args:
            url: URL to validate

        Raises:
            SecurityError: If URL is not allowed
        """
        if not url.startswith(("http://", "https://")):
            raise SecurityError("Only HTTP/HTTPS URLs are allowed")

        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            raise SecurityError("Invalid URL: no hostname")

        # Prevent SSRF to internal networks
        if hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
            raise SecurityError("Requests to localhost are not allowed")

        # Block private IP ranges
        if (
            hostname.startswith("192.168.")
            or hostname.startswith("10.")
            or hostname.startswith("172.16.")
            or hostname.startswith("172.17.")
            or hostname.startswith("172.18.")
            or hostname.startswith("172.19.")
            or hostname.startswith("172.2")
            or hostname.startswith("172.30.")
            or hostname.startswith("172.31.")
        ):
            raise SecurityError("Requests to private networks are not allowed")

        # Block other dangerous schemes
        if parsed.scheme not in ["http", "https"]:
            raise SecurityError(f"Scheme '{parsed.scheme}' is not allowed")

    def _validate_response_size(self, response: requests.Response) -> None:
        """Validate response content length.

        Args:
            response: HTTP response to validate

        Raises:
            NetworkError: If response is too large
        """
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > self.max_content_length:
            raise NetworkError(
                f"Response too large: {content_length} bytes (max: {self.max_content_length})",
                error_code="RESPONSE_TOO_LARGE",
            )

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """Make a secure GET request.

        Args:
            url: URL to request
            **kwargs: Additional arguments for requests

        Returns:
            HTTP response

        Raises:
            SecurityError: If URL is not allowed
            NetworkError: If request fails or response is invalid
        """
        try:
            self._validate_url(url)
            self.rate_limiter.check_rate_limit()

            response = self.session.get(url, timeout=self.timeout, stream=True, **kwargs)

            self._validate_response_size(response)
            response.raise_for_status()

            return response

        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {url}", error_code="TIMEOUT") from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {url}", error_code="CONNECTION_ERROR") from e
        except requests.exceptions.HTTPError as e:
            raise NetworkError(f"HTTP error {e.response.status_code}: {url}", error_code="HTTP_ERROR") from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {url}", error_code="REQUEST_FAILED") from e

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """Make a secure POST request.

        Args:
            url: URL to request
            **kwargs: Additional arguments for requests

        Returns:
            HTTP response
        """
        try:
            self._validate_url(url)
            self.rate_limiter.check_rate_limit()

            response = self.session.post(url, timeout=self.timeout, **kwargs)

            self._validate_response_size(response)
            response.raise_for_status()

            return response

        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {url}", error_code="TIMEOUT") from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {url}", error_code="CONNECTION_ERROR") from e
        except requests.exceptions.HTTPError as e:
            raise NetworkError(f"HTTP error {e.response.status_code}: {url}", error_code="HTTP_ERROR") from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {url}", error_code="REQUEST_FAILED") from e

    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()

    def __enter__(self) -> "SecureHTTPClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


# Global secure client instance
_default_client: Optional[SecureHTTPClient] = None


def get_default_client() -> SecureHTTPClient:
    """Get the default secure HTTP client."""
    global _default_client
    if _default_client is None:
        _default_client = SecureHTTPClient()
    return _default_client
