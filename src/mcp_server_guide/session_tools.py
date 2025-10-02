"""MCP tools for session-scoped project configuration."""

from typing import Dict, Any, Optional, Union
from pathlib import Path
from .session import SessionState
from .logging_config import get_logger
from .validation import validate_config_key, ConfigValidationError

logger = get_logger(__name__)


class SessionManager:
    """Singleton session manager."""

    _instance: Optional["SessionManager"] = None
    session_state: SessionState
    current_project: str

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session_state = SessionState()
            logger.debug("Session manager initialized")
        return cls._instance

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
            except (json.JSONDecodeError, OSError):
                # Handle corrupted files by backing up and starting fresh
                backup_file = config_file.with_suffix(".json.backup")
                if config_file.exists():
                    config_file.rename(backup_file)
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

    def get_current_project_safe(self) -> str:
        """Get current project with error handling for None case."""
        project = self.get_current_project()
        if project is None:
            raise ValueError("Working directory not set. Use set_directory() first.")
        return project

    def get_current_project(self) -> Optional[str]:
        """Get current project using CurrentProjectManager."""
        from .current_project_manager import CurrentProjectManager

        manager = CurrentProjectManager()
        return manager.get_current_project()

    def is_directory_set(self) -> bool:
        """Check if working directory is properly set."""
        from .current_project_manager import CurrentProjectManager

        manager = CurrentProjectManager()
        return manager.is_directory_set()

    def set_directory(self, directory: Union[str, Path]) -> None:
        """Set the working directory.

        Args:
            directory: The directory to set. Accepts either a string path or a pathlib.Path object.
        """
        from .current_project_manager import CurrentProjectManager

        # Input validation for 'directory'
        if not isinstance(directory, (str, Path)):
            raise TypeError("directory must be a string or pathlib.Path object")
        if isinstance(directory, Path):
            directory = str(directory)
        if not directory.strip():
            raise ValueError("directory must be a non-empty string or Path")

        manager = CurrentProjectManager()
        manager.set_directory(directory)

    def set_current_project(self, project_name: str) -> None:
        """Set current project using CurrentProjectManager."""
        from .current_project_manager import CurrentProjectManager

        manager = CurrentProjectManager()
        manager.set_current_project(project_name)

    def load_project_from_path(self, project_path: Any) -> None:
        """Load project configuration from path."""
        logger.debug(f"Loading project configuration from {project_path}")
        from .project_config import ProjectConfigManager

        manager = ProjectConfigManager()
        config = manager.load_config(project_path)
        if config:
            self.set_current_project(config.project)
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


def set_project_config(key: str, value: str) -> Dict[str, Any]:
    """Set configuration value for current project."""
    session_manager = SessionManager()

    # Validate the key and value before setting
    try:
        validate_config_key(key, value)
    except ConfigValidationError as e:
        return {"success": False, "error": str(e), "errors": e.errors}

    try:
        current_project = session_manager.get_current_project_safe()
        session_manager.session_state.set_project_config(current_project, key, value)
        return {"success": True, "message": f"Set {key} to '{value}' for project {current_project}"}
    except ValueError as e:
        return {"success": False, "error": str(e)}


def get_project_config() -> Dict[str, Any]:
    """Get current project's configuration."""
    session_manager = SessionManager()

    try:
        current_project = session_manager.get_current_project_safe()
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


def reset_project_config() -> Dict[str, Any]:
    """Reset current project to defaults."""
    session_manager = SessionManager()

    current_project = session_manager.get_current_project()
    if current_project in session_manager.session_state.projects:
        del session_manager.session_state.projects[current_project]

    return {"success": True, "message": f"Reset project {current_project} to defaults"}


def switch_project(project_name: str) -> Dict[str, Any]:
    """Manually switch project context."""
    if not project_name or not isinstance(project_name, str):
        raise ValueError("Project name must be a non-empty string")

    session_manager = SessionManager()
    session_manager.set_current_project(project_name)

    return {"success": True, "message": f"Switched to project {project_name}"}


def set_local_file(key: str, local_path: str) -> Dict[str, Any]:
    """Set config to use local file."""
    # Add local: prefix to the path
    local_file_path = f"local:{local_path}"
    return set_project_config(key, local_file_path)


# Backward compatibility exports
_session_state = _session_manager.session_state
_current_project = _session_manager.get_current_project()
