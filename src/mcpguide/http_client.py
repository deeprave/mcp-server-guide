"""HTTP client for remote file access (Issue 003 Phase 2)."""

from typing import Dict, Optional
import requests


class HttpError(Exception):
    """HTTP-related errors."""
    pass


class HttpClient:
    """HTTP client for fetching remote files."""

    def __init__(self, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.headers = {"User-Agent": "mcpguide/1.0"}
        if headers:
            self.headers.update(headers)

    def get(self, url: str) -> str:
        """Fetch file content via HTTP GET."""
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise HttpError(f"HTTP GET failed for {url}: {e}")

    def exists(self, url: str) -> bool:
        """Check if HTTP resource exists via HEAD request."""
        try:
            response = requests.head(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            return True
        except Exception:
            return False
