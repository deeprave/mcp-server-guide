"""Configuration access tools."""

from typing import Dict, Any, Optional


async def get_project_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get project configuration settings and values.
    This is a read-only operation that displays current configuration without making changes.

    If project cannot be determined, returns null project with instructions to fix."""
    from ..session_manager import SessionManager

    session = SessionManager()
    if not project:  # Treat None and "" the same
        try:
            project = session.get_project_name()
        except ValueError as e:
            # Return null project with error message containing fix instructions
            return {"success": False, "project": None, "error": str(e)}

    config = await session.get_or_create_project_config(project)
    return {"success": True, "project": project, "config": config.to_dict()}


async def set_project_config_values(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Set multiple project configuration values at once.
    Use when user explicitly requests updating multiple configuration settings.
    This operation modifies the project configuration and affects system behavior.

    Args:
        config_dict: Dictionary of key-value pairs to set

    Returns:
        Dictionary with success status and updated configuration
    """
    from ..session_manager import SessionManager

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
    """Update project configuration settings.
    Use when user explicitly requests changing a specific configuration value.
    This operation modifies the project configuration and affects system behavior."""

    # Note: Key and value validation will be handled by Pydantic models in future phases

    from ..session_manager import SessionManager

    session = SessionManager()
    project = session.get_project_name()

    # Check if trying to set invalid key - ProjectConfig only supports 'categories'
    if config_key == "project":
        return {
            "success": False,
            "error": "Project key is not valid for project configuration. ProjectConfig only supports 'categories'.",
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


__all__ = [
    "get_project_config",
    "set_project_config",
    "set_project_config_values",
]
