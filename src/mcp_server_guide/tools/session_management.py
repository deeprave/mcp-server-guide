"""Session management tools."""

from ..naming import config_filename
from typing import Optional, Dict, Any
from pathlib import Path
from ..session_tools import SessionManager
from ..project_config import ProjectConfigManager


async def cleanup_config(config_filename: str = config_filename()) -> Dict[str, Any]:
    """Clean up obsolete configuration fields."""
    try:
        session = SessionManager()
        await session.save_to_file(config_filename)

        return {"success": True, "message": "Configuration saved"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to save configuration"}


async def save_session(config_filename: str = config_filename()) -> Dict[str, Any]:
    """Persist current session state."""
    try:
        session = SessionManager()
        current_project = session.get_current_project()

        # Use new save method that preserves existing data
        await session.save_to_file(config_filename)

        return {"success": True, "project": current_project, "message": f"Session saved for project {current_project}"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to save session"}


def load_session(project_path: Optional[Path] = None, config_filename: str = config_filename()) -> Dict[str, Any]:
    """Load session from project."""
    try:
        if project_path is None:
            project_path = Path(".")

        session = SessionManager()
        manager = ProjectConfigManager()

        # Try to load full session state first
        if manager.load_full_session_state(project_path, session, config_filename):
            return {
                "success": True,
                "path": str(project_path),
                "project": session.get_current_project(),
                "message": f"Session loaded from {project_path}",
            }
        else:
            # Fallback to old project-based loading
            session.load_project_from_path(project_path)
            return {
                "success": True,
                "path": str(project_path),
                "project": session.get_current_project(),
                "message": f"Session loaded from {project_path}",
            }
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to load session"}


def reset_session() -> Dict[str, Any]:
    """Reset to defaults."""
    try:
        session = SessionManager()
        # Reset to default project
        session.set_current_project("mcp-server-guide")

        return {"success": True, "project": "mcp-server-guide", "message": "Session reset to defaults"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to reset session"}


__all__ = [
    "save_session",
    "load_session",
    "reset_session",
]
