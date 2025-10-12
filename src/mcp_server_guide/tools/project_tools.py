"""Project management tools."""

from typing import Dict, Any, Optional
from ..session_manager import SessionManager


async def get_current_project() -> Optional[str]:
    """Get the active project name."""
    session = SessionManager()
    return session.get_project_name()


async def switch_project(name: str) -> Dict[str, Any]:
    """Switch to a different project.

    This will:
    a. Reset the current session state config
    b. Load the config from file for the new project
    c. If config doesn't exist, initialize with default categories and save
    """
    session = SessionManager()

    try:
        # Use SessionManager's switch_project method
        await session.switch_project(name)
        return {"success": True, "project": name, "message": f"Switched to project: {name}"}
    except ValueError as e:
        return {"success": False, "error": str(e)}


__all__ = [
    "get_current_project",
    "switch_project",
]
