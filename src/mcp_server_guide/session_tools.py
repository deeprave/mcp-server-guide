"""MCP tools for session-scoped project configuration."""

import os
from typing import Dict, Any, Optional, Union
from pathlib import Path
from .session import SessionState
from .logging_config import get_logger
from .validation import validate_config_key, ConfigValidationError

logger = get_logger()


class SessionManager:
    """Singleton session manager with integrated directory and project management."""

    _instance: Optional["SessionManager"] = None
    session_state: SessionState
    _override_directory: Optional[Path]

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session_state = SessionState()
            cls._instance._override_directory = None
            logger.debug("Session manager initialized")
        return cls._instance

    @property
    def current_file_name(self) -> str:
        """Get the current project filename."""
        from .naming import current_filename

        return current_filename()

    @property
    def directory(self) -> Optional[Path]:
        """Get current directory or None if not set."""
        # If explicit directory provided, use it (for tests)
        if self._override_directory:
            return self._override_directory

        # Use ClientPath to get client working directory via MCP protocol
        try:
            from .client_path import ClientPath

            root = ClientPath.get_primary_root()
            if root:
                return root
        except Exception:
            pass

        # Check if we're in a test environment by looking for pytest
        import sys

        if "pytest" in sys.modules:
            # In tests, don't use fallbacks if ClientPath is not initialized
            return None

        # Fallback: Use PWD environment variable (same as ClientPath initialization)
        if "PWD" in os.environ:
            try:
                return Path(os.environ["PWD"]).resolve()
            except Exception:
                pass

        # Final fallback: Use current working directory
        try:
            return Path(os.getcwd()).resolve()
        except Exception:
            pass

        return None

    @property
    def current_file(self) -> Optional[Path]:
        """Get current file path or None if directory not set."""
        if self.directory is None:
            return None
        return self.directory / self.current_file_name

    def is_directory_set(self) -> bool:
        """Check if working directory is properly set."""
        return self.directory is not None

    def set_directory(self, directory: Union[str, Path]) -> None:
        """Set the working directory.

        Args:
            directory: The directory to set. Accepts either a string path or a pathlib.Path object.
        """
        # Input validation for 'directory'
        if not isinstance(directory, (str, Path)):
            raise TypeError("directory must be a string or pathlib.Path object")
        if isinstance(directory, Path):
            directory = str(directory)
        if not directory.strip():
            raise ValueError("directory must be a non-empty string or Path")

        path = Path(directory).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"Provided path '{directory}' does not exist.")
        if not path.is_dir():
            raise ValueError(f"Provided path '{directory}' is not a directory.")
        self._override_directory = path

    async def get_current_project(self) -> Optional[str]:
        """Get current project name."""
        if not self.is_directory_set():
            return None

        try:
            if self.current_file and self.current_file.exists():
                import aiofiles

                async with aiofiles.open(self.current_file, "r", encoding="utf-8") as f:
                    content = (await f.read()).strip()
                if content:
                    logger.debug(f"Read current project '{content}' from {self.current_file}")
                    return content
                else:
                    logger.debug("Empty .current file, falling back to directory name")
        except (OSError, IOError) as e:
            logger.debug(f"Failed to read {self.current_file}: {e}")

        # Fallback to directory name
        if self.directory:
            project_name = self.directory.name
            logger.debug(f"Using directory name as project: '{project_name}'")
            return project_name

        return None

    async def set_current_project(self, project_name: str) -> None:
        """Set current project name by writing to .current file.

        Args:
            project_name: Name of the project to set as current

        Raises:
            OSError: If the file cannot be written (permissions, disk space, etc.)
            ValueError: If directory is not set or project name is empty
        """
        if not self.is_directory_set():
            raise ValueError("Directory must be set before setting current project")

        if not project_name or not isinstance(project_name, str):
            raise ValueError("Project name must be a non-empty string")

        old_project = await self.get_current_project()
        self._current_project = project_name

        try:
            if self.current_file:
                self.current_file.write_text(project_name, encoding="utf-8")
                logger.debug(f"Wrote current project '{project_name}' to {self.current_file}")
        except (OSError, IOError) as e:
            logger.error(f"Failed to write current project to {self.current_file}: {e}")
            raise

        logger.info(f"Session project changed from '{old_project}' to '{project_name}'")

    async def save_to_file(self, config_file_path: str) -> None:
        """Save session state to config file, preserving existing data."""
        import json
        from pathlib import Path
        import aiofiles

        config_file = Path(config_file_path)

        # Load existing config or create new structure
        existing_config = {}
        if config_file.exists():
            try:
                async with aiofiles.open(config_file, "r", encoding="utf-8") as f:
                    content = await f.read()
                    existing_config = json.loads(content)
            except (json.JSONDecodeError, OSError) as e:
                # Handle corrupted files by backing up and starting fresh
                logger.warning(f"Config file corrupted or unreadable, backing up and starting fresh: {e}")
                backup_file = config_file.with_suffix(".json.backup")
                if config_file.exists():
                    config_file.rename(backup_file)
                    logger.info(f"Backed up corrupted config to {backup_file}")
                existing_config = {}

        # Ensure projects structure exists
        if "projects" not in existing_config:
            existing_config["projects"] = {}

        # Update with current session data (preserve existing projects)
        for project_name, project_config in self.session_state.projects.items():
            if project_name not in existing_config["projects"]:
                existing_config["projects"][project_name] = {}

            # Update only the fields that have been set, preserve others
            existing_config["projects"][project_name].update(project_config)

        # Remove current_project field if it exists (Issue 012)
        existing_config.pop("current_project", None)

        # Write updated config
        async with aiofiles.open(config_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(existing_config, indent=2))

    async def get_current_project_safe(self) -> str:
        """Get current project with error handling for None case."""
        project = await self.get_current_project()
        if project is None:
            logger.error("Cannot determine client working directory - MCP server cannot function")
            raise ValueError("Working directory not set. Use set_directory() first.")
        return project

    async def load_project_from_path(self, project_path: Any) -> None:
        """Load project configuration from path."""
        logger.debug(f"Loading project configuration from {project_path}")
        from .project_config import ProjectConfigManager

        manager = ProjectConfigManager()
        config = manager.load_config(project_path)
        if config:
            await self.set_current_project(config.project)
            # Load config into session state
            for key, value in config.to_dict().items():
                if key != "project":
                    self.session_state.set_project_config(config.project, key, value)

    def get_effective_config(self, project_name: str) -> Dict[str, Any]:
        """Get effective configuration combining file and session overrides with resolved paths."""
        config = self.session_state.get_project_config(project_name)

        # Resolve docroot to absolute path
        docroot = config.get("docroot", ".")
        if not Path(docroot).is_absolute():
            # Resolve relative paths to absolute
            config["docroot"] = str(Path(docroot).resolve())

        return config


# Global session manager instance
_session_manager = SessionManager()


async def set_project_config(key: str, value: str) -> Dict[str, Any]:
    """Set configuration value for current project."""
    session_manager = SessionManager()

    # Validate the key and value before setting
    try:
        validate_config_key(key, value)
    except ConfigValidationError as e:
        return {"success": False, "error": str(e), "errors": e.errors}

    try:
        current_project = await session_manager.get_current_project_safe()
        session_manager.session_state.set_project_config(current_project, key, value)
        return {"success": True, "message": f"Set {key} to '{value}' for project {current_project}"}
    except ValueError as e:
        return {"success": False, "error": str(e)}


async def get_project_config() -> Dict[str, Any]:
    """Get current project's configuration."""
    session_manager = SessionManager()

    try:
        current_project = await session_manager.get_current_project_safe()
        config = session_manager.session_state.get_project_config(current_project)
        return {"success": True, "project": current_project, "config": config}
    except ValueError as e:
        return {"success": False, "error": str(e)}


def list_project_configs() -> Dict[str, Any]:
    """List all project configurations."""
    session_manager = SessionManager()

    projects = {}
    for project_name in session_manager.session_state.projects:
        projects[project_name] = session_manager.session_state.get_project_config(project_name)

    return {"success": True, "projects": projects}


async def reset_project_config() -> Dict[str, Any]:
    """Reset current project to defaults."""
    session_manager = SessionManager()

    current_project = await session_manager.get_current_project()
    if current_project in session_manager.session_state.projects:
        del session_manager.session_state.projects[current_project]

    return {"success": True, "message": f"Reset project {current_project} to defaults"}


async def switch_project(project_name: str) -> Dict[str, Any]:
    """Manually switch project context."""
    if not project_name or not isinstance(project_name, str):
        raise ValueError("Project name must be a non-empty string")

    session_manager = SessionManager()
    await session_manager.set_current_project(project_name)

    return {"success": True, "message": f"Switched to project {project_name}"}


async def set_local_file(key: str, local_path: str) -> Dict[str, Any]:
    """Set config to use local file."""
    # Add local: prefix to the path
    local_file_path = f"local:{local_path}"
    return await set_project_config(key, local_file_path)


# Backward compatibility exports
_session_state = _session_manager.session_state
# Note: _current_project cannot be set at module level since get_current_project() is async
_current_project = None
