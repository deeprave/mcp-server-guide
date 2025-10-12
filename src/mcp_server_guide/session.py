"""Session-scoped project configuration management."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .session_manager import SessionManager


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
        return f"/{path[8:]}"
    elif path.startswith("file://"):
        # Relative file URL: file://relative/path → relative/path
        path = path[7:]

    # Apply basic path resolution (simplified for now)
    return path if path.startswith("/") else str(Path.cwd() / path)


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
    """Manages session-scoped project configuration for a single project."""

    def __init__(self, project_name: Optional[str] = None) -> None:
        self.project_name: str | None = project_name
        self.project_config: Dict[str, Any] = {}

    def reset_project_config(self, project_name: Optional[str] = None) -> None:
        """Reset the current project configuration."""
        self.project_name = project_name or ""
        self.project_config = {}

    def get_project_name(self) -> Optional[str]:
        """Get the current project name."""
        return self.project_name

    def set_project_name(self, project_name: str) -> None:
        """Set the current project name."""
        self.project_name = project_name

    def get_project_config(self) -> Dict[str, Any]:
        """Get configuration for the current project."""
        return self.project_config

    def merge_project_config(self, config_key: str, value: str | Dict[str, Any] | None) -> None:
        """Set configuration value for the current project."""
        self.project_config[config_key] |= value

    def set_project_config(self, config_key: str, value: str | Dict[str, Any] | None) -> None:
        """Set configuration value for the current project."""
        self.project_config[config_key] = value
