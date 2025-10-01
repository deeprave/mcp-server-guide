"""File source abstraction for hybrid file access with HTTP-aware caching."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional, Dict, TYPE_CHECKING
import aiofiles

if TYPE_CHECKING:
    from .file_cache import FileCache


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
    def from_session_path(cls, session_path: str, project_context: str) -> "FileSource":
        """Create FileSource from session path."""
        if session_path.startswith("local:"):
            return cls("local", session_path[6:])
        elif session_path.startswith("server:"):
            return cls("server", session_path[7:])
        elif session_path.startswith(("http://", "https://")):
            return cls("http", session_path)
        else:
            return cls("local", session_path)

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
    def detect_deployment_context(cls) -> Literal["local", "server"]:
        """Detect deployment context for file:// URLs."""
        # Simple heuristic: check if we're in a typical server environment
        import os

        if os.getenv("SERVER_MODE") or os.getenv("DOCKER_CONTAINER"):
            return "server"
        return "local"

    @classmethod
    def get_context_default(cls, path: str) -> "FileSource":
        """Get context-aware default FileSource."""
        context = cls.detect_deployment_context()
        return cls(context, path)


class FileAccessor:
    """File accessor with HTTP-aware caching."""

    def __init__(self, cache: Optional["FileCache"] = None, cache_dir: Optional[str] = None):
        if cache_dir and not cache:
            from .file_cache import FileCache

            cache = FileCache(cache_dir)
        self.cache = cache

    def resolve_path(self, relative_path: str, source: FileSource) -> str:
        """Resolve relative path against source base path."""
        if source.type == "http":
            # For HTTP sources, join URL components
            base = source.base_path.rstrip("/")
            path = relative_path.lstrip("/")
            return f"{base}/{path}"
        else:
            # For local/server sources, resolve filesystem paths
            base_path = Path(source.base_path)
            if not base_path.is_absolute():
                # For relative paths, resolve relative to current directory
                base_path = Path.cwd() / base_path
            return str(base_path / relative_path)

    def exists(self, relative_path: str, source: FileSource) -> bool:
        """Check if file exists."""
        if source.type == "http":
            # For HTTP, we'd need to make a HEAD request
            # For now, assume it exists (will fail on read if not)
            return True
        else:
            full_path = self.resolve_path(relative_path, source)
            return Path(full_path).exists()

    async def read_file(self, relative_path: str, source: FileSource) -> str:
        """Read file content with HTTP-aware caching."""
        if source.type == "http":
            return await self._read_http_file(relative_path, source)
        else:
            # Local/server file reading
            full_path = self.resolve_path(relative_path, source)
            async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
                return await f.read()

    async def _read_http_file(self, relative_path: str, source: FileSource) -> str:
        """Read HTTP file with caching support."""
        from .http.async_client import AsyncHTTPClient

        full_url = self.resolve_path(relative_path, source)

        # Check cache if enabled
        cached_entry = None
        if source.cache_enabled and self.cache:
            cached_entry = self.cache.get(full_url)

        # If we have cached content, try conditional request
        if cached_entry and not cached_entry.needs_validation():
            # Cache is fresh, use it
            cached_content: str = cached_entry.content
            return cached_content
        elif cached_entry:
            # Cache needs validation, make conditional request
            try:
                async with AsyncHTTPClient() as client:
                    # Try conditional request if client supports it
                    if hasattr(client, "get_conditional"):
                        # Build conditional headers from cached entry
                        conditional_headers = dict(source.auth_headers) if source.auth_headers else {}
                        if cached_entry.last_modified:
                            conditional_headers["if_modified_since"] = cached_entry.last_modified
                        if cached_entry.etag:
                            conditional_headers["if_none_match"] = cached_entry.etag

                        response = await client.get_conditional(full_url, **conditional_headers)
                        if response is None:  # 304 Not Modified
                            not_modified_content: str = cached_entry.content
                            return not_modified_content
                        content: str = response.content if hasattr(response, "content") else str(response)
                    else:
                        # Fallback to regular GET
                        response = await client.get(full_url, headers=source.auth_headers)
                        content = response.content if hasattr(response, "content") else str(response)

                    # Update cache
                    if source.cache_enabled and self.cache:
                        response_headers = response.headers if hasattr(response, "headers") else {}
                        self.cache.put(full_url, content, headers=response_headers)

                    return content
            except Exception:
                # If HTTP fails and we have cached content, use it
                if cached_entry:
                    error_fallback_content: str = cached_entry.content
                    return error_fallback_content
                raise
        else:
            # No cache, make fresh request
            try:
                async with AsyncHTTPClient() as client:
                    response = await client.get(full_url, headers=source.auth_headers)
                    content = response.content if hasattr(response, "content") else response

                    # Cache the result
                    if source.cache_enabled and self.cache:
                        response_headers = response.headers if hasattr(response, "headers") else {}
                        self.cache.put(full_url, content, headers=response_headers)

                    return content
            except Exception as e:
                raise RuntimeError(f"Failed to read HTTP file {full_url}: {e}")

    def file_exists(self, relative_path: str, source: FileSource) -> bool:
        """Check if file exists."""
        if source.type == "http":
            # For HTTP, we'd need to make a HEAD request, but for now return True
            return True
        else:
            # For local/server sources, check filesystem
            full_path = self.resolve_path(relative_path, source)
            return Path(full_path).exists()


__all__ = ["FileSource", "FileAccessor"]
