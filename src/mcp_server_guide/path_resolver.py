"""Lazy path resolution for client and server paths."""

import asyncio
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING
from .logging_config import get_logger

if TYPE_CHECKING:
    from .file_source import FileSource

logger = get_logger()


class LazyPath:
    """Path that resolves client-side paths lazily when accessed."""

    def __init__(self, path: Union[str, Path]):
        """Create a LazyPath from string or Path.

        Args:
            path: Path as string or Path object
        """
        self.path_str = str(path)
        self._resolved_path: Optional[Path] = None
        self._client_root: Optional[Path] = None
        self._file_source: Optional["FileSource"] = None
        self._file_source_lock: Optional[asyncio.Lock] = None

    async def resolve(self) -> Path:
        """Resolve the path.

        Returns:
            Resolved Path object

        Raises:
            OSError: If the path cannot be resolved (permission denied, invalid path, etc.)
            ValueError: If the path string is malformed
        """
        if self._resolved_path is not None:
            return self._resolved_path

        # Handle URI-style prefixes using FileSource logic
        if self._is_uri_style_path():
            return await self._resolve_uri_path()

        # Server-side path - resolve relative to current directory
        try:
            self._resolved_path = Path(self.path_str).expanduser().resolve()
        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Failed to resolve path '{self.path_str}': {e}")
            raise

        return self._resolved_path

    def _is_uri_style_path(self) -> bool:
        """Check if path uses URI-style prefix."""
        uri_prefixes = ["http://", "https://", "file://"]
        return any(self.path_str.startswith(prefix) for prefix in uri_prefixes)

    async def _resolve_uri_path(self) -> Path:
        """Resolve URI-style paths using FileSource logic."""
        from .file_source import FileSourceType

        file_source = await self.to_file_source()

        if file_source.type == FileSourceType.HTTP:
            # HTTP URIs resolve to themselves as Path objects
            self._resolved_path = Path(file_source.base_path)
        elif file_source.type == FileSourceType.FILE:
            # Local/client paths use current working directory
            if self._client_root is None:
                self._client_root = Path.cwd()

            self._resolved_path = self._client_root / file_source.base_path
        elif file_source.base_path.startswith("/"):
            # Absolute path
            self._resolved_path = Path(file_source.base_path)
        else:
            # Relative path
            self._resolved_path = Path(file_source.base_path).expanduser().resolve()

        return self._resolved_path

    def resolve_sync(self) -> Path:
        """Synchronous resolution - uses asyncio.run if needed.

        Returns:
            Resolved Path object

        Raises:
            OSError: If the path cannot be resolved
            ValueError: If the path string is malformed
            RuntimeError: If there's an unexpected async event loop issue
        """
        if self._resolved_path is not None:
            return self._resolved_path

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't use asyncio.run in running loop - use fallback sync resolution
                return self._resolve_sync_fallback()
            else:
                self._resolved_path = asyncio.run(self.resolve())
        except RuntimeError as e:
            # Handle event loop related errors - try to create a new event loop
            error_msg = str(e).lower()
            if "loop" in error_msg or "event" in error_msg:
                logger.debug(f"Event loop issue, creating new one: {e}")
                self._resolved_path = asyncio.run(self.resolve())
            else:
                logger.exception(f"Unexpected RuntimeError in resolve_sync for path '{self.path_str}'")
                raise
        except Exception:
            logger.exception(f"Unexpected exception in resolve_sync for path '{self.path_str}'")
            raise

        return self._resolved_path

    def _resolve_sync_fallback(self) -> Path:
        """Fallback synchronous resolution when event loop is running."""
        if self._resolved_path is not None:
            return self._resolved_path

        logger.debug(f"Using sync fallback resolution for: {self.path_str}")

        # Handle URI-style paths in sync mode
        if self._is_uri_style_path():
            from .file_source import FileSource, FileSourceType

            # Direct FileSource creation - we're in a fallback path so don't need caching
            file_source = FileSource.from_url(self.path_str)

            if file_source.type == FileSourceType.HTTP:
                self._resolved_path = Path(file_source.base_path)
            elif file_source.type == FileSourceType.FILE:
                # Use current directory as fallback for client paths
                self._resolved_path = Path.cwd() / file_source.base_path
            elif file_source.base_path.startswith("/"):
                # Absolute path
                self._resolved_path = Path(file_source.base_path)
            else:
                # Relative path
                self._resolved_path = Path(file_source.base_path).expanduser().resolve()
        else:
            self._resolved_path = Path(self.path_str).expanduser().resolve()

        return self._resolved_path

    async def to_file_source(self) -> "FileSource":
        """Convert LazyPath to FileSource representation.

        Async-safe lazy initialization of the FileSource using asyncio.Lock.

        Returns:
            FileSource instance for this path
        """
        from .file_source import FileSource

        # Fast path - no lock needed if already initialized
        if self._file_source is not None:
            return self._file_source

        # Lazy initialize the lock itself
        if self._file_source_lock is None:
            self._file_source_lock = asyncio.Lock()

        # Double-checked locking pattern for async-safe lazy initialization
        async with self._file_source_lock:
            # Check again inside the lock
            if self._file_source is None:
                self._file_source = FileSource.from_url(self.path_str)
            return self._file_source

    @classmethod
    def from_file_source(cls, file_source: "FileSource") -> "LazyPath":
        """Create LazyPath from FileSource."""
        from .file_source import FileSourceType

        # Convert FileSource back to URI format
        if file_source.type == FileSourceType.FILE:
            path_str = file_source.base_path  # Use path as-is for FILE type
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
