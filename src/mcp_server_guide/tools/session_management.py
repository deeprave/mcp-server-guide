"""Session management tools."""

import asyncio
import os
from ..naming import config_filename
from typing import Optional, Dict, Any, Callable, Union
from functools import wraps
from pathlib import Path
from ..session_tools import SessionManager
from ..project_config import ProjectConfigManager


def require_directory_set(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to ensure directory is set before running tool."""

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            session = SessionManager()
            if not session.is_directory_set():
                return {
                    "success": False,
                    "error": "Working directory not set. Please use 'set directory /path/to/project' first.",
                    "blocked": True,
                }
            return await func(*args, **kwargs)

        return async_wrapper
    else:

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            session = SessionManager()
            if not session.is_directory_set():
                return {
                    "success": False,
                    "error": "Working directory not set. Please use 'set directory /path/to/project' first.",
                    "blocked": True,
                }
            return func(*args, **kwargs)

        return sync_wrapper


async def set_directory(directory: Union[str, Path]) -> Dict[str, Any]:
    """Set the working directory for the MCP server."""
    try:
        # Handle None values before os.fspath
        if directory is None:
            return {"success": False, "error": "Directory must be a non-empty string"}

        # Use os.fspath for idiomatic Path/str conversion
        directory_str = os.fspath(directory)

        if not directory_str or not directory_str.strip():
            return {"success": False, "error": "Directory must be a non-empty string"}

        path = Path(directory_str).expanduser().resolve()
        if not path.exists():
            return {"success": False, "error": f"Directory does not exist: {directory}"}
        if not path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {directory}"}

        session = SessionManager()
        session.set_directory(str(path))

        project = await session.get_current_project()
        return {"success": True, "message": f"Working directory set to: {path}", "project": project}
    except asyncio.CancelledError:
        # Re-raise cancellation to allow proper cleanup
        raise
    except (OSError, PermissionError, ValueError) as e:
        return {"success": False, "error": f"Failed to set directory: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error setting directory: {e}"}


@require_directory_set
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
        current_project = await session.get_current_project()

        # Use new save method that preserves existing data
        await session.save_to_file(config_filename)

        return {"success": True, "project": current_project, "message": f"Session saved for project {current_project}"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to save session"}


async def load_session(project_path: Optional[Path] = None, config_filename: str = config_filename()) -> Dict[str, Any]:
    """Load session from project."""
    try:
        if project_path is None:
            project_path = Path(".")

        # Validate that path is a directory
        if project_path.exists() and not project_path.is_dir():
            return {"success": False, "error": f"Session path '{project_path}' exists but is not a directory"}

        session = SessionManager()
        manager = ProjectConfigManager()

        if not await manager.load_full_session_state(project_path, session, config_filename):
            # Fallback to old project-based loading
            await session.load_project_from_path(project_path)
        return {
            "success": True,
            "path": str(project_path),
            "project": await session.get_current_project(),
            "message": f"Session loaded from {project_path}",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to load session"}


async def reset_session() -> Dict[str, Any]:
    """Reset to defaults."""
    try:
        session = SessionManager()
        # Reset to current directory name
        current_project = os.path.basename(os.getcwd())

        # Set current project
        await session.set_current_project(current_project)

        # Reset project config to defaults
        from ..session_tools import reset_project_config

        await reset_project_config()

        return {"success": True, "project": current_project, "message": "Session reset to defaults"}
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to reset session"}


__all__ = [
    "save_session",
    "load_session",
    "reset_session",
]
