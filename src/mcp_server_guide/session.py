"""Session-scoped project configuration management."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .session_tools import SessionManager


# Global session instance
_session_manager: Optional["SessionManager"] = None


def get_session() -> Optional["SessionManager"]:
    """Get the current session manager instance."""
    return _session_manager


def set_session(session: "SessionManager") -> None:
    """Set the current session manager instance."""
    global _session_manager
    _session_manager = session


@dataclass
class ProjectContext:
    """Project context information."""

    name: str
    path: str

    @classmethod
    def detect(cls, path: str) -> "ProjectContext":
        """Detect project context from directory path."""
        project_path = Path(path)
        return cls(name=project_path.name, path=str(project_path))


def resolve_session_path(path: str, project_context: str) -> str:
    """Resolve path with context-aware file URL schemes for session configuration."""
    return resolve_server_path(path, project_context)


def resolve_server_path(path: str, project_context: str) -> str:
    """Resolve path following server process context."""
    # Handle file:// URL normalization
    if path.startswith("file:///"):
        # Absolute file URL: file:///absolute/path → /absolute/path
        return "/" + path[8:]  # Remove "file:///" and add back leading /
    elif path.startswith("file://"):
        # Relative file URL: file://relative/path → relative/path
        path = path[7:]

    # Apply basic path resolution (simplified for now)
    if path.startswith("/"):
        return path  # Absolute path
    else:
        # Relative path - resolve relative to current working directory
        return str(Path.cwd() / path)


def resolve_client_path(path: str) -> str:
    """Resolve path relative to client's working directory."""
    # Simplified implementation - in real MCP this would communicate with client
    if path.startswith("/"):
        return path  # Absolute path
    else:
        # For now, assume client working directory is same as server
        return str(Path.cwd() / path)


def validate_session_path(path: str) -> bool:
    """Validate path with support for file URL schemes."""
    if not path:
        return False

    if path.startswith("file:///"):
        # Absolute file URL - should have content after file:///
        return len(path) > 8  # More than just "file:///"
    elif path.startswith("file://"):
        # Relative file URL - always valid format
        return True
    else:
        # Basic path validation
        return True


class SessionState:
    """Manages session-scoped project configurations."""

    def __init__(self) -> None:
        self.projects: Dict[str, Dict[str, Any]] = {}
        self._projects_lock = asyncio.Lock()
        self._defaults = {
            "docroot": ".",
        }

    async def get_project_config(self, project_name: str) -> Dict[str, Any]:
        """Get configuration for a project."""
        # Ensure project exists in session state with thread-safe access
        async with self._projects_lock:
            if project_name not in self.projects:
                self.projects[project_name] = {}
            project_config = self.projects[project_name].copy()

        # Merge with defaults (outside lock for performance)
        config = self._defaults.copy()
        config.update(project_config)
        return config

    async def set_project_config(self, project_name: str, config_key: str, value: str | Dict[str, Any] | None) -> None:
        """Set configuration value for a project."""
        async with self._projects_lock:
            if project_name not in self.projects:
                self.projects[project_name] = {}
            self.projects[project_name][config_key] = value
