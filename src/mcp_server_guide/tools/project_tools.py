"""Project management tools."""

from typing import List, Dict, Any
from ..session_tools import SessionManager


def get_current_project() -> str:
    """Get the active project name."""
    session = SessionManager()
    return session.get_current_project()


def switch_project(name: str) -> Dict[str, Any]:
    """Switch to a different project."""
    session = SessionManager()
    session.set_current_project(name)
    return {"success": True, "project": name, "message": f"Switched to project: {name}"}


def list_projects() -> List[str]:
    """List available projects."""
    session = SessionManager()
    # Get all projects from session state
    projects = list(session.session_state.projects.keys())
    if not projects:
        projects = [session.get_current_project()]
    return projects


__all__ = [
    "get_current_project",
    "switch_project",
    "list_projects",
]
