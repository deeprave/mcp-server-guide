"""Session-scoped project configuration management."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .session_manager import SessionManager

from .project_config import ProjectConfig


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
        self.project_config: ProjectConfig = ProjectConfig(categories={})

    def reset_project_config(self, project_name: Optional[str] = None) -> None:
        """Reset the current project configuration."""
        self.project_name = project_name or ""
        self.project_config = ProjectConfig(categories={})

    def get_project_name(self) -> Optional[str]:
        """Get the current project name."""
        return self.project_name

    def set_project_name(self, project_name: str) -> None:
        """Set the current project name."""
        self.project_name = project_name

    def get_project_config(self) -> ProjectConfig:
        """Get configuration for the current project."""
        return self.project_config

    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        from pydantic import ValidationError

        # Validate with Pydantic - this checks both key validity and value structure
        try:
            ProjectConfig.model_validate(config)
        except ValidationError as e:
            # Convert Pydantic error to ValueError with helpful message
            raise ValueError(f"Invalid project configuration: {e}") from e

    def merge_project_config(self, value: Optional[Dict[str, Any]]) -> None:
        """Merge a configuration set for the current project.

        Uses Pydantic validation to ensure the value is valid
        according to the ProjectConfig schema.

        Args:
            value: Configuration dict to merge

        Raises:
            ValueError: If the config is invalid (wraps Pydantic ValidationError)
        """
        if value:
            # Convert current config to dict, deep merge, then validate and convert back
            def deep_merge(d1: Dict[str, Any], d2: Dict[str, Any]) -> Dict[str, Any]:
                for k, v in d2.items():
                    if (
                        k in d1
                        and isinstance(d1[k], dict)
                        and isinstance(v, dict)
                    ):
                        d1[k] = deep_merge(d1[k], v)
                    else:
                        d1[k] = v
                return d1

            current_dict = self.project_config.to_dict()
            updated_dict = deep_merge(current_dict, value)
            self._validate_config(updated_dict)
            # If validation passed, set it
            self.project_config = ProjectConfig.from_dict(updated_dict)

    def set_project_config(self, config_key: str, value: str | Dict[str, Any] | None) -> None:
        """Set a configuration value for the current project.

        Uses Pydantic validation to ensure both the key and value are valid
        according to the ProjectConfig schema.

        Args:
            config_key: Configuration key to set
            value: Configuration value

        Raises:
            ValueError: If the config is invalid (wraps Pydantic ValidationError)
        """
        # Build updated config dict with the new value
        current_dict = self.project_config.to_dict()
        updated_dict = {**current_dict, config_key: value}
        self._validate_config(updated_dict)
        # If validation passed, update the ProjectConfig
        self.project_config = ProjectConfig.from_dict(updated_dict)
