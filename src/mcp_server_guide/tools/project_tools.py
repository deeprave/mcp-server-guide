"""Project management tools."""

from typing import List, Dict, Any, Optional
from ..session_tools import SessionManager
from .session_management import save_session


async def get_current_project() -> Optional[str]:
    """Get the active project name."""
    session = SessionManager()
    return await session.get_current_project()


async def switch_project(name: str) -> Dict[str, Any]:
    """Switch to a different project."""
    session = SessionManager()

    # Check if project exists
    project_exists = name in session.session_state.projects

    # Set current project
    await session.set_current_project(name)

    if not project_exists:
        # Auto-create built-in categories for new project
        _create_builtin_categories(session, name)

    # Save session state after switching
    await save_session()

    return {"success": True, "project": name, "message": f"Switched to project: {name}"}


def _create_builtin_categories(session: SessionManager, project_name: str) -> None:
    """Create built-in categories with default values and auto_load = true."""
    builtin_defaults = {
        "guide": {
            "dir": "guide/",
            "patterns": ["guidelines"],
            "description": "Development guidelines",
            "auto_load": True,
        },
        "lang": {
            "dir": "lang/",
            "patterns": ["none"],
            "description": "Language-specific guidelines",
            "auto_load": True,
        },
        "context": {
            "dir": "context/",
            "patterns": ["project-context"],
            "description": "Project-specific guidelines",
            "auto_load": True,
        },
    }

    # Create categories config
    categories = {}
    for name, config in builtin_defaults.items():
        categories[name] = config

    # Set categories in project config
    session.session_state.set_project_config(project_name, "categories", categories)


async def list_projects() -> List[str]:
    """List available projects."""
    session = SessionManager()
    # Get all projects from session state
    projects = list(session.session_state.projects.keys())
    if not projects:
        current = await session.get_current_project()
        if current:
            projects = [current]
    return projects


__all__ = [
    "get_current_project",
    "switch_project",
    "list_projects",
]
