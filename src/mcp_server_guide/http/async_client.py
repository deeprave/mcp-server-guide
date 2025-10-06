"""Async HTTP client with security features."""

import asyncio
from typing import Dict, Any, Optional, Type
from types import TracebackType
from urllib.parse import urlparse
import aiohttp
from ..logging_config import get_logger

logger = get_logger()


class AsyncHTTPClient:
    """Async HTTP client with SSRF protection and rate limiting."""

    def __init__(self, timeout: int = 30, max_redirects: int = 5):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_redirects = max_redirects
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            timeout=self.timeout, connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
        )
        return self

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    def _validate_url(self, url: str) -> None:
        """Validate URL for SSRF protection."""
        parsed = urlparse(url)

        if not parsed.scheme or parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

        if not parsed.netloc:
            raise ValueError("URL must have a valid hostname")

        # Basic SSRF protection - block private IPs
        hostname = parsed.hostname
        if hostname in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("Access to localhost is not allowed")

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """Perform async GET request."""
        self._validate_url(url)

        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        logger.debug(f"Making async GET request to: {url}")

        try:
            async with self._session.get(url, headers=headers) as response:
                response.raise_for_status()
                content = await response.text()
                logger.debug(f"Received {len(content)} characters from {url}")
                return content
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for URL: {url}")
            raise

    async def post(self, url: str, data: Any = None, headers: Optional[Dict[str, str]] = None) -> str:
        """Perform async POST request."""
        self._validate_url(url)

        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        logger.debug(f"Making async POST request to: {url}")

        try:
            async with self._session.post(url, json=data, headers=headers) as response:
                response.raise_for_status()
                content = await response.text()
                logger.debug(f"Received {len(content)} characters from {url}")
                return content
        except aiohttp.ClientError as e:
            logger.error(f"HTTP POST request failed: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"POST request timeout for URL: {url}")
            raise
