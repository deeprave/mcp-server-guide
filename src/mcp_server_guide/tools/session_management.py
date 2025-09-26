"""Session management tools."""

from typing import Optional, Dict, Any
from pathlib import Path
from ..session_tools import SessionManager
from ..project_config import ProjectConfigManager


def save_session(config_filename: str = ".mcp-server-guide.config.json") -> Dict[str, Any]:
    """Persist current session state."""
    try:
        session = SessionManager()
        current_project = session.get_current_project()

        # Save to current directory by default
        project_path = Path(".")
        manager = ProjectConfigManager()
        manager.save_full_session_state(project_path, session, config_filename)

        return {"success": True, "project": current_project, "message": f"Session saved for project {current_project}"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to save session"}


def load_session(
    project_path: Optional[Path] = None, config_filename: str = ".mcp-server-guide.config.json"
) -> Dict[str, Any]:
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
