"""Lazy path resolution for client and server paths."""

import asyncio
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING
from .client_path import ClientPath
from .logging_config import get_logger

if TYPE_CHECKING:
    from .file_source import FileSource

logger = get_logger()


class LazyPath:
    """Path that resolves client-side paths lazily when accessed."""

    def __init__(self, path_str: str):
        self.path_str = path_str
        self._resolved_path: Optional[Path] = None
        self._client_root: Optional[Path] = None
        self._file_source: Optional["FileSource"] = None

    async def resolve(self) -> Path:
        """Resolve the path, handling client: prefixes."""
        if self._resolved_path is not None:
            return self._resolved_path

        # Handle URI-style prefixes using FileSource logic
        if self._is_uri_style_path():
            return await self._resolve_uri_path()

        # Handle legacy client: prefix
        if self.path_str.startswith("client:"):
            # Client-side path - need client working directory
            if self._client_root is None:
                self._client_root = ClientPath.get_primary_root()

            if self._client_root is None:
                raise ValueError(f"Cannot resolve client path '{self.path_str}': no client working directory available")

            # Remove client: prefix and resolve relative to client root
            relative_path = self.path_str[7:]  # Remove "client:"
            self._resolved_path = self._client_root / relative_path
        else:
            # Server-side path - resolve relative to current directory
            self._resolved_path = Path(self.path_str).expanduser().resolve()

        return self._resolved_path

    def _is_uri_style_path(self) -> bool:
        """Check if path uses URI-style prefix."""
        uri_prefixes = ["client://", "local://", "server://", "http://", "https://", "file://"]
        return any(self.path_str.startswith(prefix) for prefix in uri_prefixes)

    async def _resolve_uri_path(self) -> Path:
        """Resolve URI-style paths using FileSource logic."""
        from .file_source import FileSourceType

        file_source = self.to_file_source()

        if file_source.type == FileSourceType.HTTP:
            # HTTP URIs resolve to themselves as Path objects
            self._resolved_path = Path(file_source.base_path)
        elif file_source.type == FileSourceType.LOCAL:
            # Local/client paths need client working directory
            if self._client_root is None:
                self._client_root = ClientPath.get_primary_root()

            if self._client_root is None:
                raise ValueError(f"Cannot resolve client path '{self.path_str}': no client working directory available")

            self._resolved_path = self._client_root / file_source.base_path
        else:  # SERVER
            # Server paths resolve relative to current directory
            if file_source.base_path.startswith("/"):
                # Absolute path
                self._resolved_path = Path(file_source.base_path)
            else:
                # Relative path
                self._resolved_path = Path(file_source.base_path).expanduser().resolve()

        return self._resolved_path

    def resolve_sync(self) -> Path:
        """Synchronous resolution - uses asyncio.run if needed."""
        if self._resolved_path is not None:
            return self._resolved_path

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't use asyncio.run in running loop - use fallback sync resolution
                return self._resolve_sync_fallback()
            else:
                self._resolved_path = asyncio.run(self.resolve())
        except RuntimeError:
            self._resolved_path = asyncio.run(self.resolve())

        return self._resolved_path

    def _resolve_sync_fallback(self) -> Path:
        """Fallback synchronous resolution when event loop is running."""
        if self._resolved_path is not None:
            return self._resolved_path

        logger.debug(f"Using sync fallback resolution for: {self.path_str}")

        # Handle URI-style paths in sync mode
        if self._is_uri_style_path():
            from .file_source import FileSourceType

            file_source = self.to_file_source()

            if file_source.type == FileSourceType.HTTP:
                self._resolved_path = Path(file_source.base_path)
            elif file_source.type == FileSourceType.LOCAL:
                # Use current directory as fallback for client paths
                self._resolved_path = Path.cwd() / file_source.base_path
            else:  # SERVER
                # For server paths, resolve relative to current directory
                if file_source.base_path.startswith("/"):
                    # Absolute path
                    self._resolved_path = Path(file_source.base_path)
                else:
                    # Relative path
                    self._resolved_path = Path(file_source.base_path).expanduser().resolve()
        elif self.path_str.startswith("client:"):
            relative_path = self.path_str[7:]
            self._resolved_path = Path.cwd() / relative_path
        else:
            self._resolved_path = Path(self.path_str).expanduser().resolve()

        return self._resolved_path

    def to_file_source(self) -> "FileSource":
        """Convert LazyPath to FileSource representation."""
        from .file_source import FileSource

        if self._file_source is not None:
            return self._file_source

        self._file_source = FileSource.from_url(self.path_str)
        return self._file_source

    @classmethod
    def from_file_source(cls, file_source: "FileSource") -> "LazyPath":
        """Create LazyPath from FileSource."""
        from .file_source import FileSourceType

        # Convert FileSource back to URI format
        if file_source.type == FileSourceType.LOCAL:
            path_str = f"client://{file_source.base_path}"
        elif file_source.type == FileSourceType.SERVER:
            path_str = f"server://{file_source.base_path}"
        elif file_source.type == FileSourceType.HTTP:
            path_str = file_source.base_path  # HTTP URLs are stored as-is
        else:
            path_str = file_source.base_path

        lazy_path = cls(path_str)
        lazy_path._file_source = file_source
        return lazy_path

    def __str__(self) -> str:
        return self.path_str

    def __repr__(self) -> str:
        return f"LazyPath('{self.path_str}')"


def create_lazy_path(path: Union[str, Path]) -> LazyPath:
    """Create a LazyPath from string or Path."""
    return LazyPath(str(path))
