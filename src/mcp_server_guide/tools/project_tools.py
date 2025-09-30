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

    # Check if project exists
    project_exists = name in session.session_state.projects

    # Set current project
    session.set_current_project(name)

    if not project_exists:
        # Auto-create built-in categories for new project
        _create_builtin_categories(session, name)

    return {"success": True, "project": name, "message": f"Switched to project: {name}"}


def _create_builtin_categories(session: SessionManager, project_name: str) -> None:
    """Create built-in categories with default values and auto_load = true."""
    builtin_defaults = {
        "guide": {
            "dir": "guide/",
            "patterns": ["guidelines"],
            "description": "Development methodology, TDD approach, and SOLID/YAGNI guardrails",
            "auto_load": True
        },
        "lang": {
            "dir": "lang/",
            "patterns": ["none"],
            "description": "Language-specific coding standards, best practices, required tools, and syntax guidelines",
            "auto_load": True
        },
        "context": {
            "dir": "context/",
            "patterns": ["project-context"],
            "description": "Project-specific information, issue management, and product specifications",
            "auto_load": True
        }
    }

    # Create categories config
    categories = {}
    for name, config in builtin_defaults.items():
        categories[name] = config

    # Set categories in project config
    session.session_state.set_project_config(project_name, "categories", categories)


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
