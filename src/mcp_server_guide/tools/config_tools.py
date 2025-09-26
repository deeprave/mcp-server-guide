"""Configuration access tools."""

from typing import Dict, Any, List, Optional
from ..session_tools import SessionManager


def get_project_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get project configuration."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    config = session.session_state.get_project_config(project)
    config["project"] = project  # Ensure project name is included
    return config


def set_project_config_values(
    config_dict: Dict[str, Any], project: Optional[str] = None, config_filename: str = ".mcp-server-guide.config.json"
) -> Dict[str, Any]:
    """Set multiple project configuration values at once.

    Args:
        config_dict: Dictionary of key-value pairs to set
        project: Project name (uses current if None)
        config_filename: Configuration file name

    Returns:
        Dictionary with operation results
    """
    session = SessionManager()

    if project is None:
        project = session.get_current_project()

    results = []
    success_count = 0

    for key, value in config_dict.items():
        try:
            result = set_project_config(key, value, project, config_filename)
            if result.get("success"):
                success_count += 1
            results.append(
                {
                    "key": key,
                    "value": value,
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                }
            )
        except Exception as e:
            results.append({"key": key, "value": value, "success": False, "message": f"Error setting {key}: {str(e)}"})

    return {
        "success": success_count == len(config_dict),
        "project": project,
        "total_keys": len(config_dict),
        "success_count": success_count,
        "results": results,
        "message": f"Set {success_count}/{len(config_dict)} configuration values for project {project}",
    }


def set_project_config(
    key: str, value: Any, project: Optional[str] = None, config_filename: str = ".mcp-server-guide.config.json"
) -> Dict[str, Any]:
    """Update project settings."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    session.session_state.set_project_config(project, key, value)

    # Auto-save configuration changes (except project changes)
    if key != "project":
        try:
            from .session_management import save_session

            save_session(config_filename)
        except Exception as e:
            # Log error but don't fail the config change
            from ..logging_config import get_logger

            logger = get_logger(__name__)
            logger.warning(f"Failed to auto-save session after config change: {e}")

    return {
        "success": True,
        "project": project,
        "key": key,
        "value": value,
        "message": f"Set {key} = {value} for project {project}",
    }


def get_effective_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get merged configuration (file + session)."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    return session.get_effective_config(project)


def get_tools(project: Optional[str] = None) -> List[str]:
    """Get project-specific tools list."""
    config = get_project_config(project)
    result = config.get("tools", [])
    return list(result) if result else []


def set_tools(tools_array: List[str], project: Optional[str] = None) -> Dict[str, Any]:
    """Set tools for project."""
    return set_project_config("tools", tools_array, project)


__all__ = [
    "get_project_config",
    "set_project_config",
    "set_project_config_values",
    "get_effective_config",
    "get_tools",
    "set_tools",
]
