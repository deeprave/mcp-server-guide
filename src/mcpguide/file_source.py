"""File source abstraction for hybrid file access with HTTP-aware caching."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional, Dict
from .session import resolve_session_path


@dataclass
class FileSource:
    """File source configuration."""

    type: Literal["local", "server", "http"]
    base_path: str
    cache_ttl: int = 3600
    cache_enabled: bool = True
    auth_headers: Optional[Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_url(cls, url: str) -> "FileSource":
        """Create FileSource from URL, integrating Issue 002 file:// support."""
        if url.startswith("local:"):
            return cls("local", url[6:])
        elif url.startswith("server:"):
            return cls("server", url[7:])
        elif url.startswith(("http://", "https://")):
            return cls("http", url)
        elif url.startswith("file://"):
            # Context-aware file URLs (from Issue 002)
            return cls._from_file_url(url)
        else:
            # Context-aware default (from Issue 002)
            return cls.get_context_default(url)

    @classmethod
    def _from_file_url(cls, url: str) -> "FileSource":
        """Handle file:// URLs with context awareness."""
        context = cls.detect_deployment_context()
        if url.startswith("file:///"):
            # Absolute file URL
            path = "/" + url[8:]  # Remove "file:///" and add back leading /
        else:
            # Relative file URL
            path = url[7:]  # Remove "file://"

        return cls(context, path)

    @classmethod
    def get_context_default(cls, path: str) -> "FileSource":
        """Get context-aware default source."""
        context = cls.detect_deployment_context()
        return cls(context, path)

    @classmethod
    def detect_deployment_context(cls) -> Literal["local", "server"]:
        """Detect deployment context (simplified for now)."""
        # For now, assume server context
        # In real implementation, this would detect local vs remote deployment
        return "server"

    @classmethod
    def from_session_path(cls, session_path: str, project_context: str) -> "FileSource":
        """Create FileSource from Issue 002 session path."""
        # Use Issue 002's session resolution to determine the actual path
        resolved_path = resolve_session_path(session_path, project_context)

        if session_path.startswith("local:"):
            return cls("local", resolved_path)
        elif session_path.startswith(("http://", "https://")):
            return cls("http", session_path)
        else:
            return cls("server", resolved_path)


class FileAccessor:
    """Unified file access interface with HTTP-aware caching."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir
        self._cache = None

    @property
    def cache(self):
        """Lazy-load cache only when needed."""
        if self._cache is None and self.cache_dir:
            from .file_cache import FileCache

            self._cache = FileCache(cache_dir=self.cache_dir)
        return self._cache

    def resolve_path(self, relative_path: str, source: FileSource) -> str:
        """Resolve relative path against file source."""
        if source.type == "http":
            # HTTP URL joining
            base = source.base_path.rstrip("/")
            path = relative_path.lstrip("/")
            return f"{base}/{path}"
        else:
            # Local/server path joining
            return str(Path(source.base_path) / relative_path)

    def file_exists(self, relative_path: str, source: FileSource) -> bool:
        """Check if file exists."""
        if source.type == "http":
            # HTTP existence checking
            from .http_client import HttpClient

            full_url = self.resolve_path(relative_path, source)
            client = HttpClient(timeout=30, headers=source.auth_headers)
            return client.exists(full_url)
        else:
            # Local/server file existence
            full_path = self.resolve_path(relative_path, source)
            return Path(full_path).exists()

    def read_file(self, relative_path: str, source: FileSource) -> str:
        """Read file content with HTTP-aware caching."""
        if source.type == "http":
            return self._read_http_file(relative_path, source)
        else:
            # Local/server file reading
            full_path = self.resolve_path(relative_path, source)
            return Path(full_path).read_text()

    def _read_http_file(self, relative_path: str, source: FileSource) -> str:
        """Read HTTP file with caching support."""
        from .http_client import HttpClient, HttpError

        full_url = self.resolve_path(relative_path, source)
        client = HttpClient(timeout=30, headers=source.auth_headers)

        # Check cache if enabled
        cached_entry = None
        if source.cache_enabled and self.cache:
            cached_entry = self.cache.get(full_url)

        # If we have cached content, try conditional request
        if cached_entry and not cached_entry.needs_validation():
            # Cache is fresh, use it
            return cached_entry.content
        elif cached_entry:
            # Cache needs validation, make conditional request
            try:
                response = client.get_conditional(
                    full_url, if_modified_since=cached_entry.last_modified, if_none_match=cached_entry.etag
                )

                if response is None:
                    # 304 Not Modified, use cached content
                    return cached_entry.content
                else:
                    # Content changed, update cache and return new content
                    if source.cache_enabled and self.cache:
                        self.cache.put(full_url, response.content, response.headers)
                    return response.content

            except HttpError:
                # Network error, fall back to cache if available
                if cached_entry:
                    return cached_entry.content
                raise
        else:
            # No cache, make regular request
            response = client.get(full_url)

            # Cache the response if caching is enabled
            if source.cache_enabled and self.cache:
                # Handle both HttpResponse objects and strings (for backward compatibility)
                if hasattr(response, "content"):
                    self.cache.put(full_url, response.content, response.headers)
                    return response.content
                else:
                    # Old string-based response (for tests)
                    self.cache.put(full_url, response, {})
                    return response

            # Return content
            if hasattr(response, "content"):
                return response.content
            else:
                return response
