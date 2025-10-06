"""HTTP client for remote file access with conditional requests (Issue 003 Phase 2-3)."""

from dataclasses import dataclass
from typing import Dict, Optional
import requests
from .logging_config import get_logger

logger = get_logger()


class HttpError(Exception):
    """HTTP-related errors."""

    pass


@dataclass
class HttpResponse:
    """HTTP response with content and headers."""

    content: str
    headers: Dict[str, str]


class HttpClient:
    """HTTP client for fetching remote files."""

    def __init__(self, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.headers = {"User-Agent": "mcp-server-guide/1.0"}
        if headers:
            self.headers.update(headers)
        logger.debug(f"HTTP client initialized with timeout={timeout}")

    def get(self, url: str) -> HttpResponse:
        """Fetch file content via HTTP GET."""
        logger.debug(f"HTTP GET: {url}")
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            logger.debug(f"HTTP GET successful: {url} ({len(response.text)} chars)")
            return HttpResponse(content=response.text, headers=dict(response.headers))
        except Exception as e:
            logger.warning(f"HTTP GET failed for {url}: {e}")
            raise HttpError(f"HTTP GET failed for {url}: {e}")

    def get_conditional(
        self, url: str, if_modified_since: Optional[str] = None, if_none_match: Optional[str] = None
    ) -> Optional[HttpResponse]:
        """Make conditional HTTP request. Returns None for 304 Not Modified."""
        logger.debug(f"HTTP conditional GET: {url}")
        conditional_headers = self.headers.copy()

        if if_modified_since:
            conditional_headers["If-Modified-Since"] = if_modified_since

        if if_none_match:
            conditional_headers["If-None-Match"] = if_none_match

        try:
            response = requests.get(url, timeout=self.timeout, headers=conditional_headers)

            if response.status_code == 304:
                logger.debug(f"HTTP 304 Not Modified: {url}")
                # Not Modified
                return None

            response.raise_for_status()
            return HttpResponse(content=response.text, headers=dict(response.headers))
        except Exception as e:
            raise HttpError(f"HTTP conditional GET failed for {url}: {e}")

    def exists(self, url: str) -> bool:
        """Check if HTTP resource exists via HEAD request."""
        try:
            response = requests.head(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            return True
        except Exception:
            return False
