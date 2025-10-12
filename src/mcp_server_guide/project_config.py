"""Persistent project configuration (Issue 004)."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

from .naming import mcp_name
from .file_lock import lock_update
from .path_resolver import LazyPath


class Category(BaseModel):
    """Category configuration for organizing source code."""

    dir: str = Field(..., description="Directory path relative to project root")
    patterns: List[str] = Field(default_factory=list, description="File patterns to match")
    description: str = Field(default="", description="Human-readable description of the category")
    auto_load: Optional[bool] = Field(None, description="Whether to include in 'all' grouping")

    @field_validator("dir")
    @classmethod
    def validate_dir(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Directory path cannot be empty")
        # Normalize path separators and remove redundant slashes
        normalized = v.strip().replace("\\", "/")
        # Remove leading slash to ensure relative paths
        if normalized.startswith("/"):
            normalized = normalized[1:]
        # Ensure it ends with / for consistency
        if normalized and not normalized.endswith("/"):
            normalized += "/"
        return normalized

    @field_validator("patterns")
    @classmethod
    def validate_patterns(cls, v: List[str]) -> List[str]:
        if not v:  # Empty list is allowed
            return v
        for pattern in v:
            if not isinstance(pattern, str):
                raise ValueError("File patterns must be strings")
            if not pattern.strip():
                raise ValueError("File patterns cannot be empty")
            # Basic glob pattern validation
            if ".." in pattern:
                raise ValueError("File patterns cannot contain path traversal sequences")
        return [p.strip() for p in v]

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        # Description is optional and flexible - just strip whitespace
        return v.strip() if v else ""


class ProjectConfig(BaseModel):
    """Project configuration containing only categories."""

    docroot: Optional[str] = Field(None, description="Document root directory path")
    categories: Dict[str, Category] = Field(default_factory=dict, description="Category definitions")

    @field_validator("docroot")
    @classmethod
    def validate_docroot(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            return None  # Empty string becomes None
        # Basic path validation
        if ".." in v:
            raise ValueError("Document root cannot contain path traversal sequences")
        return v.strip()

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, v: Dict[str, Category]) -> Dict[str, Category]:
        if not isinstance(v, dict):
            raise ValueError("Categories must be a dictionary")

        # Validate category names
        for name in v.keys():
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
                raise ValueError(
                    f'Category name "{name}" must start with a letter and contain only alphanumeric characters, underscores, and hyphens'
                )
            if len(name) > 30:
                raise ValueError(f'Category name "{name}" cannot exceed 30 characters')

        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values and empty lists."""
        data = self.model_dump(exclude_none=True)
        return {k: v for k, v in data.items() if v is not None and v != [] and v != {}}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        """Create ProjectConfig from dictionary data."""
        return cls(**data)


class ConfigFile(BaseModel):
    """Complete configuration file with global settings and projects."""

    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True,  # Validate on assignment
    )

    docroot: Optional[str] = Field(".", description="Global project root directory")
    projects: Dict[str, ProjectConfig] = Field(default_factory=dict, description="Project configurations")

    @field_validator("docroot")
    @classmethod
    def validate_docroot(cls, v: Optional[str]) -> str:
        if v is None:
            return "."  # Default to current directory
        if not v.strip():
            return "."
        # Basic path validation
        if ".." in v:
            raise ValueError("Global document root cannot contain path traversal sequences")
        return v.strip()

    @field_validator("projects")
    @classmethod
    def validate_projects(cls, v: Dict[str, ProjectConfig]) -> Dict[str, ProjectConfig]:
        if not isinstance(v, dict):
            raise ValueError("Projects must be a dictionary")

        # Validate project names (the keys)
        for name in v.keys():
            if not name or not name.strip():
                raise ValueError("Project name cannot be empty")
            if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", name):
                raise ValueError(
                    f'Project name "{name}" must start with alphanumeric and contain only alphanumeric characters, underscores, and hyphens'
                )
            if len(name) > 50:
                raise ValueError(f'Project name "{name}" cannot exceed 50 characters')

        return v


def _get_global_config_path() -> Path:
    """Get a platform-aware global config file path."""
    import os
    from pathlib import Path

    # Platform-aware global config directory
    if os.name == "nt":  # Windows
        config_dir = Path(os.environ["APPDATA"]) / mcp_name()
    else:  # Unix/Linux/macOS
        config_dir = Path.home() / ".config" / mcp_name()

    # Ensure config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir / "config.yaml"


def _save_config_locked(config_file: Path, project_name: str, config: ProjectConfig) -> None:
    """Internal function to save config while holding file lock."""
    # Load existing config structure
    existing_config = ConfigFile(docroot=".", projects={})
    if config_file.exists():
        try:
            with open(config_file) as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict):  # Handle empty YAML files and ensure it's a dict
                    existing_config = ConfigFile(**data)
        except yaml.YAMLError as e:
            # Handle YAML parsing errors with specific message
            from .logging_config import get_logger

            logger = get_logger()
            logger.warning(f"Invalid YAML in config file {config_file}: {e}. Creating new configuration.")
        except (OSError, IOError) as e:
            # Handle file I/O errors
            from .logging_config import get_logger

            logger = get_logger()
            logger.warning(f"Cannot read config file {config_file}: {e}. Creating new configuration.")
        except (ValueError, TypeError) as e:
            # Handle Pydantic validation errors
            from .logging_config import get_logger

            logger = get_logger()
            logger.warning(f"Invalid configuration structure in {config_file}: {e}. Creating new configuration.")

    # Validate the project config before saving
    try:
        # This will trigger Pydantic validation
        validated_config = ProjectConfig(**config.model_dump())
    except ValueError as e:
        raise ValueError(f"Invalid project configuration for '{project_name}': {e}") from e

    # Update the specific project using the provided project name
    existing_config.projects[project_name] = validated_config

    # Save updated config in YAML format
    try:
        with open(config_file, "w") as f:
            yaml.dump(
                existing_config.model_dump(exclude_none=True), f, default_flow_style=False, sort_keys=False, indent=2
            )
    except (OSError, IOError) as e:
        raise IOError(f"Cannot write to config file {config_file}: {e}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Cannot serialize configuration to YAML: {e}") from e


def _load_config_locked(config_file: Path, project_name: str) -> Optional[ProjectConfig]:
    """Internal function to load config while holding file lock."""
    if not config_file.exists():
        return None

    try:
        with open(config_file) as f:
            data = yaml.safe_load(f)

        # Handle empty YAML files and ensure it's a dict
        if not data or not isinstance(data, dict):
            from .logging_config import get_logger

            logger = get_logger()
            logger.warning(f"Config file {config_file} is empty or contains invalid data")
            return None

        # Load from projects structure
        if "projects" in data and project_name in data["projects"]:
            project_data = data["projects"][project_name]
            try:
                return ProjectConfig(**project_data)
            except ValueError as e:
                from .logging_config import get_logger

                logger = get_logger()
                logger.error(f"Invalid configuration for project '{project_name}': {e}")
                return None

        return None

    except yaml.YAMLError as e:
        from .logging_config import get_logger

        logger = get_logger()
        logger.error(f"YAML parsing error in config file {config_file}: {e}")
        return None
    except (OSError, IOError) as e:
        from .logging_config import get_logger

        logger = get_logger()
        logger.error(f"Cannot read config file {config_file}: {e}")
        return None
    except Exception as e:
        from .logging_config import get_logger

        logger = get_logger()
        logger.error(f"Unexpected error loading config from {config_file}: {e}")
        return None


class ProjectConfigManager:
    """Manager for persistent project configuration."""

    def __init__(self) -> None:
        """Initialize project config manager."""
        self._config_filename: Optional[Path] = None  # Lazy initialization

    def set_config_filename(self, filename: str | LazyPath | Path | None) -> None:
        """Set the config filename explicitly."""
        if filename:
            # Convert LazyPath to Path if needed
            if isinstance(filename, LazyPath):
                self._config_filename = Path(str(filename)).resolve()
            else:
                self._config_filename = Path(filename).resolve()

    def get_config_filename(self) -> Path:
        """Get config filename - returns full global path."""
        if self._config_filename is None:
            self._config_filename = _get_global_config_path()
        return self._config_filename

    def save_config(self, project_name: str, config: ProjectConfig) -> None:
        """Save project configuration to file with explicit project name."""
        config_file = Path(self.get_config_filename())
        config_file.parent.mkdir(parents=True, exist_ok=True)
        lock_update(config_file, _save_config_locked, project_name, config)

    def load_config(self, project_name: str) -> Optional[ProjectConfig]:
        """Load project configuration from file.

        Args:
            project_name: Name of the project to load (must not be empty)

        Returns:
            ProjectConfig if found, None otherwise
        """
        # Convert to string if Path object
        project_name_str = project_name or ""
        if not project_name_str or not project_name_str.strip():
            raise ValueError("Project name cannot be empty")

        config_file = Path(self.get_config_filename())

        # Use file locking to ensure thread-safe reads
        return lock_update(config_file, _load_config_locked, project_name_str)
