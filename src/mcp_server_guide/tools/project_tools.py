"""Project management tools."""

from typing import Dict, Any, Optional
from copy import deepcopy
from ..logging_config import get_logger

logger = get_logger()


async def get_current_project() -> Optional[str]:
    """Get the active project name."""
    from ..session_manager import SessionManager

    session = SessionManager()
    result = session.get_project_name()
    logger.debug(f"get_project_name returned type: {type(result)}, value: {result}")
    return result


async def switch_project(name: str) -> Dict[str, Any]:
    """Switch to a different project.

    This will:
    a. Reset the current session state config
    b. Load the config from file for the new project
    c. If config doesn't exist, initialize with default categories and save
    """
    from ..session_manager import SessionManager

    session = SessionManager()

    try:
        # Use SessionManager's switch_project method
        await session.switch_project(name)
        return {"success": True, "project": name, "message": f"Switched to project: {name}"}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def clone_project(
    source_project: str, target_project: Optional[str] = None, force: bool = False
) -> Dict[str, Any]:
    """Clone categories and collections from source project to target project.

    Args:
        source_project: Name of the source project to clone from
        target_project: Name of the target project (defaults to current project)
        force: If True, overwrite target even if it has custom content

    Returns:
        Dict with success status and error message if failed
    """
    from ..session_manager import SessionManager
    from ..project_config import ProjectConfig

    session = SessionManager()

    # Load source config
    source_config = await session.load_config(source_project)
    if source_config is None:
        return {"success": False, "error": f"Source project '{source_project}' not found"}

    # Determine target project
    if target_project is None:
        target_project = session.get_project_name()

    # Load target config
    target_config = await session.load_config(target_project)

    # Check if target has custom content (unless force=True)
    if not force and target_config is not None:
        default_keys = set(SessionManager.default_categories().keys())
        target_keys = set(target_config.categories.keys())
        has_custom_categories = target_keys != default_keys
        has_collections = len(target_config.collections) > 0

        if has_custom_categories or has_collections:
            return {
                "success": False,
                "error": f"Target project '{target_project}' has custom content. Use force=True to overwrite",
            }

    # Create new config with cloned content
    new_config = ProjectConfig(
        categories=deepcopy(source_config.categories), collections=deepcopy(source_config.collections)
    )

    # Save target config
    await session.save_config(target_project, new_config)

    # Update session state if target is current project
    if target_project == session.get_project_name():
        session._session_state.project_config = new_config

    return {"success": True, "message": f"Cloned '{source_project}' to '{target_project}'"}


__all__ = [
    "get_current_project",
    "switch_project",
    "clone_project",
]
