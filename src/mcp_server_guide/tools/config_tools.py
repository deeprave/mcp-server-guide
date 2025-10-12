"""Configuration access tools."""

from typing import Dict, Any, Optional
from ..session_manager import SessionManager


async def get_project_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get project configuration."""
    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    config = await session.get_or_create_project_config(project)
    return {"success": True, "project": project, "config": config}


async def set_project_config_values(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Set multiple project configuration values at once.

    Args:
        config_dict: Dictionary of key-value pairs to set

    Returns:
        Dictionary with success status and updated configuration
    """
    session = SessionManager()
    project = session.get_project_name()

    # Note: Configuration validation will be handled by Pydantic models in future phases

    results = []
    success_count = 0

    for key, value in config_dict.items():
        try:
            result = await set_project_config(key, value)
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


async def set_project_config(config_key: str, value: Any) -> Dict[str, Any]:
    """Update project settings."""

    # Note: Key and value validation will be handled by Pydantic models in future phases

    session = SessionManager()
    project = session.get_project_name()

    # Check if trying to change an immutable project key
    if config_key == "project":
        current_config = await session.get_or_create_project_config(project)
        if "project" in current_config and current_config["project"] != value:
            return {
                "success": False,
                "error": f"Project key is immutable. Cannot change from "
                f"'{current_config['project']}' to '{value}'. Create a new project instead.",
                "key": config_key,
                "value": value,
            }

    session.session_state.set_project_config(config_key, value)

    return {
        "success": True,
        "project": project,
        "key": config_key,
        "value": value,
        "message": f"Set {config_key} = {value} for project {project}",
    }


async def get_effective_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get merged configuration (file + session)."""
    session = SessionManager()
    if project is None:
        project = session.get_project_name()

    return await session.get_effective_config(project)


__all__ = [
    "get_project_config",
    "set_project_config",
    "set_project_config_values",
    "get_effective_config",
]
