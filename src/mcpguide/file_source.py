"""File source abstraction for hybrid file access (Issue 003 Phase 1)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from .session import resolve_session_path


@dataclass
class FileSource:
    """File source configuration."""
    type: Literal["local", "server", "http"]
    base_path: str
    cache_ttl: int = 3600
    cache_enabled: bool = True

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
    """Unified file access interface."""

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
            # HTTP existence checking comes in Phase 2
            return True
        else:
            # Local/server file existence
            full_path = self.resolve_path(relative_path, source)
            return Path(full_path).exists()

    def read_file(self, relative_path: str, source: FileSource) -> str:
        """Read file content."""
        if source.type == "http":
            # HTTP reading comes in Phase 2
            raise NotImplementedError("HTTP file reading not yet implemented")
        else:
            # Local/server file reading
            full_path = self.resolve_path(relative_path, source)
            return Path(full_path).read_text()
