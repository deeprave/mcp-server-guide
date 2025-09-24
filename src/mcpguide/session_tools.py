"""MCP tools for session-scoped project configuration."""

from typing import Dict, Any
from .session import SessionState

# Global session state (in real MCP server this would be managed differently)
_session_state = SessionState()
_current_project = "mcpguide"  # Default project


def set_project_config(key: str, value: str) -> Dict[str, Any]:
    """Set configuration value for current project."""
    global _session_state, _current_project

    _session_state.set_project_config(_current_project, key, value)

    return {
        "success": True,
        "message": f"Set {key} to '{value}' for project {_current_project}"
    }


def get_project_config() -> Dict[str, Any]:
    """Get current project's configuration."""
    global _session_state, _current_project

    config = _session_state.get_project_config(_current_project)

    return {
        "success": True,
        "project": _current_project,
        "config": config
    }


def list_project_configs() -> Dict[str, Any]:
    """List all project configurations."""
    global _session_state

    projects = {}
    for project_name in _session_state.projects:
        projects[project_name] = _session_state.get_project_config(project_name)

    return {
        "success": True,
        "projects": projects
    }


def reset_project_config() -> Dict[str, Any]:
    """Reset current project to defaults."""
    global _session_state, _current_project

    if _current_project in _session_state.projects:
        del _session_state.projects[_current_project]

    return {
        "success": True,
        "message": f"Reset project {_current_project} to defaults"
    }


def switch_project(project_name: str) -> Dict[str, Any]:
    """Manually switch project context."""
    global _current_project

    _current_project = project_name

    return {
        "success": True,
        "message": f"Switched to project {project_name}"
    }


def set_local_file(key: str, local_path: str) -> Dict[str, Any]:
    """Set config to use local file."""
    # Add local: prefix to the path
    local_file_path = f"local:{local_path}"
    return set_project_config(key, local_file_path)
