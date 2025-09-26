"""Directory-scoped current project tracking."""

import logging
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class CurrentProjectManager:
    """Manages current project tracking using .mcp-server-guide.current files.

    This class provides directory-scoped project tracking to avoid concurrency
    issues with global configuration files. Each directory can have its own
    current project, stored in a .mcp-server-guide.current file.
    """

    CURRENT_FILE_NAME = ".mcp-server-guide.current"

    def __init__(self, directory: Optional[Path] = None):
        """Initialize manager for specified directory.

        Args:
            directory: Directory to manage project for (defaults to current working directory)
        """
        self.directory = directory or Path.cwd()
        self.current_file = self.directory / self.CURRENT_FILE_NAME

    def get_current_project(self) -> str:
        """Get current project name from .current file or fallback to directory name.

        Returns:
            Current project name, either from .current file or directory name as fallback
        """
        try:
            if self.current_file.exists():
                content = self.current_file.read_text(encoding="utf-8").strip()
                if content:  # Handle empty files
                    logger.debug(f"Read current project '{content}' from {self.current_file}")
                    return content
                else:
                    logger.debug("Empty .current file, falling back to directory name")
        except (OSError, IOError) as e:
            logger.warning(f"Failed to read {self.current_file}: {e}")

        # Fallback to directory name
        project_name = self.directory.name
        logger.debug(f"Using directory name as project: '{project_name}'")
        return project_name

    def set_current_project(self, project_name: str) -> None:
        """Set current project name by writing to .current file.

        Args:
            project_name: Name of the project to set as current

        Raises:
            OSError: If the file cannot be written (permissions, disk space, etc.)
        """
        if not project_name or not project_name.strip():
            raise ValueError("Project name cannot be empty")

        try:
            self.current_file.write_text(project_name.strip(), encoding="utf-8")
            logger.debug(f"Set current project to '{project_name}' in {self.current_file}")
        except (OSError, IOError) as e:
            logger.error(f"Failed to write current project to {self.current_file}: {e}")
            raise

    def clear_current_project(self) -> None:
        """Remove the .current file, reverting to directory name fallback."""
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
        return self.current_file.exists()
