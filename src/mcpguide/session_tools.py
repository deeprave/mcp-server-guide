"""MCP tools for session-scoped project configuration."""

from typing import Dict, Any
from .session import SessionState


class SessionManager:
    """Singleton session manager."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session_state = SessionState()
            cls._instance.current_project = "mcpguide"
        return cls._instance

    def get_current_project(self) -> str:
        return self.current_project

    def set_current_project(self, project_name: str) -> None:
        self.current_project = project_name

    def load_project_from_path(self, project_path) -> None:
        """Load project configuration from path."""
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

    session_manager.session_state.set_project_config(session_manager.current_project, key, value)

    return {
        "success": True,
        "message": f"Set {key} to '{value}' for project {session_manager.current_project}"
    }


def get_project_config() -> Dict[str, Any]:
    """Get current project's configuration."""
    session_manager = SessionManager()

    config = session_manager.session_state.get_project_config(session_manager.current_project)

    return {
        "success": True,
        "project": session_manager.current_project,
        "config": config
    }


def list_project_configs() -> Dict[str, Any]:
    """List all project configurations."""
    session_manager = SessionManager()

    projects = {}
    for project_name in session_manager.session_state.projects:
        projects[project_name] = session_manager.session_state.get_project_config(project_name)

    return {
        "success": True,
        "projects": projects
    }


def reset_project_config() -> Dict[str, Any]:
    """Reset current project to defaults."""
    session_manager = SessionManager()

    if session_manager.current_project in session_manager.session_state.projects:
        del session_manager.session_state.projects[session_manager.current_project]

    return {
        "success": True,
        "message": f"Reset project {session_manager.current_project} to defaults"
    }


def switch_project(project_name: str) -> Dict[str, Any]:
    """Manually switch project context."""
    session_manager = SessionManager()
    session_manager.current_project = project_name

    return {
        "success": True,
        "message": f"Switched to project {project_name}"
    }


def set_local_file(key: str, local_path: str) -> Dict[str, Any]:
    """Set config to use local file."""
    # Add local: prefix to the path
    local_file_path = f"local:{local_path}"
    return set_project_config(key, local_file_path)


# Backward compatibility exports
_session_state = _session_manager.session_state
_current_project = _session_manager.current_project
