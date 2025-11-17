"""Lazy path resolution for client and server paths."""

import os
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

    def expanduser(self) -> str:
        """Expand ~ and ~user constructions.

        Returns:
            Path string with ~ expanded
        """
        return Path(self.path_str).expanduser().as_posix()

    def expandvars(self) -> str:
        """Expand environment variables of form $var and ${var}.

        Returns:
            Path string with environment variables expanded
        """
        return os.path.expandvars(self.path_str)

    def resolve(self, *, strict: bool = False, expand: bool = True) -> Path:
        """Resolve the path.

        Args:
            strict: If True, raise FileNotFoundError if the path doesn't exist (passed to Path.resolve())
            expand: If True, expand ~ and environment variables before resolving (default: True)

        Returns:
            Resolved Path object

        Raises:
            OSError: If the path cannot be resolved (permission denied, invalid path, etc.)
            ValueError: If the path string is malformed
            FileNotFoundError: If strict=True and the path doesn't exist
        """
        if self._resolved_path is not None:
            return self._resolved_path

        # Handle URI-style prefixes using FileSource logic
        if self._is_uri_style_path():
            return self._resolve_uri_path()

        # Server-side path - resolve relative to current directory
        try:
            path_str = self.path_str
            if expand:
                path_str = os.path.expandvars(path_str)
                path_str = str(Path(path_str).expanduser())
            self._resolved_path = Path(path_str).resolve(strict=strict)
        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Failed to resolve path '{self.path_str}': {e}")
            raise

        return self._resolved_path

    def _is_uri_style_path(self) -> bool:
        """Check if path uses URI-style prefix."""
        uri_prefixes = ["http://", "https://", "file://"]
        return any(self.path_str.startswith(prefix) for prefix in uri_prefixes)

    def _resolve_uri_path(self) -> Path:
        """Resolve URI-style paths using FileSource logic."""
        from .file_source import FileSourceType

        file_source = self.to_file_source()

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

    def to_file_source(self) -> "FileSource":
        """Convert LazyPath to FileSource representation.

        Returns:
            FileSource instance for this path
        """
        from .file_source import FileSource

        # Simple synchronous initialization
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

    def is_absolute(self) -> bool:
        """Check if path is absolute, accounting for ~ and ${VAR} expansions.

        Returns:
            True if the path is absolute after variable expansion
        """
        expanded = Path(os.path.expandvars(self.path_str)).expanduser()
        return expanded.is_absolute()

    def __str__(self) -> str:
        return self.path_str

    def __repr__(self) -> str:
        return f"LazyPath('{self.path_str}')"
