"""Directory-scoped current project tracking."""

import logging
import os
from pathlib import Path
from typing import Optional, Union

from .naming import current_filename

logger = logging.getLogger(__name__)


class CurrentProjectManager:
    """Manages current project tracking using .mcp-server-guide.current files.

    This class provides directory-scoped project tracking to avoid concurrency
    issues with global configuration files. Each directory can have its own
    current project, stored in a .mcp-server-guide.current file.
    """

    CURRENT_FILE_NAME = current_filename()

    def __init__(self, directory: Optional[Path] = None):
        """Initialize manager for specified directory.

        Args:
            directory: Directory to manage project for. If None, uses PWD environment variable
        """
        self._override_directory = directory

    @property
    def directory(self) -> Optional[Path]:
        """Get current directory or None if not set."""
        # If explicit directory provided, use it (for tests)
        if self._override_directory:
            return self._override_directory

        # Try PWD environment variable (client's working directory)
        pwd = os.environ.get("PWD")
        if pwd:
            pwd_path = Path(pwd).resolve()
            if pwd_path.exists():
                return pwd_path
        # Fallback to current working directory if PWD is unset or invalid
        return Path.cwd()

    @property
    def current_file(self) -> Optional[Path]:
        """Get current file path or None if directory not set."""
        if self.directory is None:
            return None
        return self.directory / self.CURRENT_FILE_NAME

    def is_directory_set(self) -> bool:
        """Check if working directory is properly set."""
        return self.directory is not None

    def set_directory(self, directory: Union[str, Path]) -> None:
        """Explicitly set the working directory.

        Accepts either a string or Path object for the directory.
        Normalizes the provided directory path to an absolute path.

        Raises:
            ValueError: If the provided path does not exist or is not a directory.
        """
        path = Path(directory).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"Provided path '{directory}' does not exist.")
        if not path.is_dir():
            raise ValueError(f"Provided path '{directory}' is not a directory.")
        self._override_directory = path

    def get_current_project(self) -> Optional[str]:
        """Get current project name or None if directory not set."""
        if not self.is_directory_set():
            return None

        try:
            if self.current_file and self.current_file.exists():
                content = self.current_file.read_text(encoding="utf-8").strip()
                if content:
                    logger.debug(f"Read current project '{content}' from {self.current_file}")
                    return content
                else:
                    logger.debug("Empty .current file, falling back to directory name")
        except (OSError, IOError) as e:
            logger.warning(f"Failed to read {self.current_file}: {e}")

        # Fallback to directory name
        if self.directory:
            project_name = self.directory.name
            logger.debug(f"Using directory name as project: '{project_name}'")
            return project_name

        return None

    def set_current_project(self, project_name: str) -> None:
        """Set current project name by writing to .current file.

        Args:
            project_name: Name of the project to set as current

        Raises:
            OSError: If the file cannot be written (permissions, disk space, etc.)
            ValueError: If directory is not set or project name is empty
        """
        if not self.is_directory_set():
            raise ValueError("Directory must be set before setting current project")

        if not project_name or not project_name.strip():
            raise ValueError("Project name cannot be empty")

        try:
            if self.current_file is None:
                raise ValueError("Working directory not set. Use set_directory() first.")
            self.current_file.write_text(project_name.strip(), encoding="utf-8")
            logger.debug(f"Set current project to '{project_name}' in {self.current_file}")
        except (OSError, IOError) as e:
            logger.error(f"Failed to write current project to {self.current_file}: {e}")
            raise

    def clear_current_project(self) -> None:
        """Remove the .current file, reverting to directory name fallback."""
        if not self.is_directory_set() or not self.current_file:
            return

        try:
            if self.current_file.exists():
                self.current_file.unlink()
                logger.debug(f"Cleared current project file {self.current_file}")
        except (OSError, IOError) as e:
            logger.warning(f"Failed to remove {self.current_file}: {e}")

    def has_current_file(self) -> bool:
        """Check if a .current file exists in the directory.

        Returns:
            True if .current file exists, False otherwise
        """
        return self.current_file is not None and self.current_file.exists()
