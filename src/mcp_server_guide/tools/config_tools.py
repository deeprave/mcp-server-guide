"""Configuration access tools."""

from typing import Dict, Any, Optional
from ..session_tools import SessionManager
from ..validation import validate_config, ConfigValidationError
from ..naming import config_filename


def get_project_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get project configuration."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    config = session.session_state.get_project_config(project)
    # Only set project name if not already explicitly set in config
    if "project" not in config:
        config["project"] = project
    return config


async def set_project_config_values(
    config_dict: Dict[str, Any], project: Optional[str] = None, config_filename_param: Optional[str] = None
) -> Dict[str, Any]:
    """Set multiple project configuration values at once.

    Args:
        config_dict: Dictionary of key-value pairs to set
        project: Project name (uses current if None)
        config_filename_param: Config filename (uses default if None)

    Returns:
        Dictionary with success status and updated configuration
    """
    if config_filename_param is None:
        config_filename_param = config_filename()
    session = SessionManager()

    if project is None:
        project = session.get_current_project()

    # Validate entire configuration before setting any values
    try:
        # Get current config and merge with new values for validation
        current_config = get_project_config(project)
        merged_config = {**current_config, **config_dict}
        validate_config(merged_config)
    except ConfigValidationError as e:
        return {
            "success": False,
            "error": f"Configuration validation failed: {str(e)}",
            "errors": e.errors,
            "project": project,
        }

    results = []
    success_count = 0

    for key, value in config_dict.items():
        try:
            result = await set_project_config(key, value, project, config_filename_param)
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


async def set_project_config(
    config_key: str, value: Any, project: Optional[str] = None, config_filename_param: Optional[str] = None
) -> Dict[str, Any]:
    """Update project settings."""
    if config_filename_param is None:
        config_filename_param = config_filename()

    # Validate the key and value before setting
    try:
        from ..validation import validate_config_key, ConfigValidationError

        validate_config_key(config_key, value)
    except ConfigValidationError as e:
        return {"success": False, "error": str(e), "errors": e.errors, "key": config_key, "value": value}

    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    # Check if trying to change an immutable project key
    if config_key == "project":
        current_config = session.session_state.get_project_config(project)
        if "project" in current_config and current_config["project"] != value:
            return {
                "success": False,
                "error": f"Project key is immutable. Cannot change from '{current_config['project']}' to '{value}'. Create a new project instead.",
                "key": config_key,
                "value": value,
            }

    session.session_state.set_project_config(project, config_key, value)

    # Auto-save configuration changes (except project changes)
    if config_key != "project":
        try:
            from .session_management import save_session

            await save_session(config_filename_param)
        except Exception as e:
            # Log error but don't fail the config change
            from ..logging_config import get_logger

            logger = get_logger(__name__)
            logger.warning(f"Failed to auto-save session after config change: {e}")

    return {
        "success": True,
        "project": project,
        "key": config_key,
        "value": value,
        "message": f"Set {config_key} = {value} for project {project}",
    }


def get_effective_config(project: Optional[str] = None) -> Dict[str, Any]:
    """Get merged configuration (file + session)."""
    session = SessionManager()
    if project is None:
        project = session.get_current_project()

    return session.get_effective_config(project)


__all__ = [
    "get_project_config",
    "set_project_config",
    "set_project_config_values",
    "get_effective_config",
]
