"""MCP tools for session-scoped project configuration."""

from typing import Dict, Any, Optional
from .session import SessionState
from .logging_config import get_logger

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
            # Use CurrentProjectManager to get the actual current project
            from .current_project_manager import CurrentProjectManager

            manager = CurrentProjectManager()
            cls._instance.current_project = manager.get_current_project()
            logger.debug("Session manager initialized")
        return cls._instance

    def save_to_file(self, config_file_path: str) -> None:
        """Save session state to config file, preserving existing data."""
        import json
        from pathlib import Path

        config_file = Path(config_file_path)

        # Load existing config or create new structure
        existing_config = {}
        if config_file.exists():
            try:
                existing_config = json.loads(config_file.read_text())
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
        config_file.write_text(json.dumps(existing_config, indent=2))

    def get_current_project(self) -> str:
        """Get current project using CurrentProjectManager."""
        from .current_project_manager import CurrentProjectManager

        manager = CurrentProjectManager()
        current = manager.get_current_project()
        # Sync instance attribute
        self.current_project = current
        return current

    def set_current_project(self, project_name: str) -> None:
        """Set current project using CurrentProjectManager."""
        from .current_project_manager import CurrentProjectManager

        manager = CurrentProjectManager()
        manager.set_current_project(project_name)
        # Update instance attribute for backward compatibility
        self.current_project = project_name

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
        """Get effective configuration combining file and session overrides."""
        return self.session_state.get_project_config(project_name)


# Global session manager instance
_session_manager = SessionManager()


def set_project_config(key: str, value: str) -> Dict[str, Any]:
    """Set configuration value for current project."""
    session_manager = SessionManager()

    session_manager.session_state.set_project_config(session_manager.get_current_project(), key, value)

    return {"success": True, "message": f"Set {key} to '{value}' for project {session_manager.get_current_project()}"}


def get_project_config() -> Dict[str, Any]:
    """Get current project's configuration."""
    session_manager = SessionManager()

    config = session_manager.session_state.get_project_config(session_manager.get_current_project())

    return {"success": True, "project": session_manager.get_current_project(), "config": config}


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
