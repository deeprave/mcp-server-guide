"""File source abstraction for hybrid file access with HTTP-aware caching."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

import aiofiles

if TYPE_CHECKING:
    from .file_cache import FileCache


class FileSourceType(Enum):
    """File source type enumeration."""

    FILE = "file"
    HTTP = "http"

    def __str__(self) -> str:
        """Return string representation of the enum value."""
        return self.value


@dataclass
class FileSource:
    """File source configuration."""

    type: FileSourceType
    base_path: str
    cache_ttl: int = 3600
    cache_enabled: bool = True
    auth_headers: Optional[Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_url(cls, url: str) -> "FileSource":
        """Create FileSource from URL, integrating Issue 002 file:// support."""
        if url.startswith(("http://", "https://")):
            return cls(FileSourceType.HTTP, url)
        elif url.startswith("file:") or "://" not in url:
            # Context-aware file URLs (from Issue 002)
            return cls._from_file_url(url)
        else:
            # Unknown scheme - raise error for malformed prefixes
            scheme = url.split("://", 1)[0]
            raise ValueError(f"Unsupported URL scheme: {scheme}://")

    @classmethod
    def from_session_path(cls, session_path: str, project_context: str) -> "FileSource":
        """Create FileSource from session path."""
        if session_path.startswith(("http://", "https://")):
            return cls(FileSourceType.HTTP, session_path)
        else:
            return cls(FileSourceType.FILE, session_path)

    @classmethod
    def _from_file_url(cls, url: str) -> "FileSource":
        """Handle file:// URLs - always creates FILE type source."""
        if url.startswith("file:///"):
            path = f"/{url[8:]}"
        elif url.startswith("file://"):
            path = url[7:]  # Remove "file://"
        elif url.startswith("file:"):
            # Just "file:" prefix
            path = url[5:]  # Remove "file:"
        else:
            path = url

        return cls(FileSourceType.FILE, path)

    @classmethod
    def get_context_default(cls, path: str) -> "FileSource":
        """Get default FileSource - always creates FILE type source."""
        return cls(FileSourceType.FILE, path)


class FileAccessor:
    """File accessor with HTTP-aware caching."""

    def __init__(self, cache: Optional["FileCache"] = None, cache_dir: Optional[str] = None):
        if cache_dir and not cache:
            from .file_cache import FileCache

            cache = FileCache(cache_dir)
        self.cache = cache

    def resolve_path(self, relative_path: str, source: FileSource) -> str:
        """Resolve relative path against source base path."""
        if source.type == FileSourceType.HTTP:
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
        # For HTTP, we'd need to make a HEAD request
        # For now, assume it exists (will fail on read if not)
        # sourcery skip: class-extract-method
        if source.type == FileSourceType.HTTP:
            return True
        full_path = self.resolve_path(relative_path, source)
        return Path(full_path).exists()

    async def read_file(self, relative_path: str, source: FileSource) -> str:
        """Read file content with HTTP-aware caching."""
        if source.type == FileSourceType.HTTP:
            return await self._read_http_file(relative_path, source)
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
                raise RuntimeError(f"Failed to read HTTP file {full_url}: {e}") from e

    def file_exists(self, relative_path: str, source: FileSource) -> bool:
        """Check if file exists."""
        if source.type == FileSourceType.HTTP:
            # For HTTP, we'd need to make a HEAD request, but for now return True
            # Sadly, AsyncHTTPClient().head is not implemented
            return True
        # For local/server sources, check filesystem
        full_path = self.resolve_path(relative_path, source)
        return Path(full_path).exists()


__all__ = ["FileSourceType", "FileSource", "FileAccessor"]
