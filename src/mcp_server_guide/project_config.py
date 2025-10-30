"""Persistent project configuration (Issue 004)."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime, timezone
import re

from .naming import mcp_name
from .file_lock import lock_update
from .path_resolver import LazyPath

logger = logging.getLogger(__name__)

# Configure YAML to handle datetime objects automatically
yaml.add_representer(datetime, lambda dumper, data: dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat()))


class Category(BaseModel):
    """Category configuration for organizing source code.

    A category can either:
    - Point to HTTP resources via 'url' field
    - Point to local files via 'dir' and 'patterns' fields
    But not both.
    """

    url: Optional[str] = Field(None, description="HTTP URL for remote resources")
    dir: Optional[str] = Field(None, description="Directory path relative to project root")
    patterns: Optional[List[str]] = Field(None, description="File patterns to match")
    description: str = Field(default="", description="Human-readable description of the category")

    def model_post_init(self, __context: Any) -> None:
        """Validate that category has either url OR dir/patterns, but not both."""
        has_url = self.url is not None
        has_dir = self.dir is not None
        has_patterns = self.patterns is not None and len(self.patterns) > 0

        if has_url and (has_dir or has_patterns):
            raise ValueError("Category cannot have both 'url' and 'dir'/'patterns' fields")

        if not has_url and not has_dir:
            raise ValueError("Category must have either 'url' or 'dir' field")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("URL cannot be empty")
        # Basic URL validation
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("dir")
    @classmethod
    def validate_dir(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
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
    def validate_patterns(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
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


class Collection(BaseModel):
    """Collection of categories for logical grouping."""

    categories: List[str] = Field(description="List of category names in this collection")
    description: str = Field(default="", description="Human-readable description of the collection")

    # Metadata fields
    source_type: Literal["spec_kit", "user"] = Field(default="user", description="Source that created this collection")
    spec_kit_version: Optional[str] = Field(
        default=None, description="Spec-kit version (only for spec_kit source_type)"
    )
    created_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Collection creation timestamp"
    )
    modified_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Collection last modified timestamp"
    )

    @model_validator(mode="after")
    def validate_spec_kit_version(self) -> "Collection":
        """Validate spec_kit_version is only set for spec_kit source_type."""
        if self.spec_kit_version is not None and self.source_type != "spec_kit":
            raise ValueError("spec_kit_version can only be set when source_type is 'spec_kit'")
        if self.spec_kit_version is not None and not self.spec_kit_version.strip():
            raise ValueError("spec_kit_version cannot be empty")
        if self.spec_kit_version:
            self.spec_kit_version = self.spec_kit_version.strip()
        return self

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("Categories must be a list")
        if not v:
            raise ValueError("Collection must contain at least one category")

        # Validate category name format
        from .utils.validation import is_valid_name

        for category_name in v:
            if not isinstance(category_name, str):
                raise ValueError("Category names must be strings")
            if not is_valid_name(category_name):
                raise ValueError(
                    f'Category name "{category_name}" must contain only letters, numbers, dash, and underscore'
                )

        # Remove duplicates while preserving order
        seen = set()
        unique_categories = []
        for cat in v:
            if cat not in seen:
                seen.add(cat)
                unique_categories.append(cat)

        return unique_categories

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        return v.strip() if v else ""


class ProjectConfig(BaseModel):
    """Project configuration containing categories and collections."""

    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True,  # Validate on assignment
    )

    categories: Dict[str, Category] = Field(default_factory=dict, description="Category definitions")
    collections: Dict[str, Collection] = Field(
        default_factory=dict,
        description=(
            "Collection definitions. "
            "Collection names must start with a letter, may contain only alphanumeric characters, underscores, and hyphens, "
            "and cannot exceed 30 characters."
        ),
    )

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump to ensure collections are included."""
        data = super().model_dump(*args, **kwargs)
        # Always include collections
        if "collections" not in data:
            data["collections"] = {}
        return data

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, v: Dict[str, Any]) -> Dict[str, Category]:
        if not isinstance(v, dict):
            raise ValueError("Categories must be a dictionary")

        # Validate category names and ensure all values are Category objects
        category_objects = {}
        for name, cat_data in v.items():
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
                raise ValueError(
                    f'Category name "{name}" must start with a letter and contain only alphanumeric characters, underscores, and hyphens'
                )
            if len(name) > 30:
                raise ValueError(f'Category name "{name}" cannot exceed 30 characters')

            if isinstance(cat_data, dict):
                logger.debug(f"Converting dict to Category object for '{name}'")
                try:
                    category_objects[name] = Category(**cat_data)
                except Exception as e:
                    raise ValueError(f"Invalid category data for '{name}': {e}") from e
            elif isinstance(cat_data, Category):
                category_objects[name] = cat_data
            else:
                raise TypeError(
                    f"Category '{name}' must be a dictionary or Category object, got {type(cat_data).__name__}"
                )

        return category_objects

    @field_validator("collections")
    @classmethod
    def validate_collections(cls, v: Dict[str, Any]) -> Dict[str, Collection]:
        if not isinstance(v, dict):
            truncated = str(v)
            if len(truncated) > 100:
                truncated = truncated[:100] + "..."
            raise ValueError(f"Collections must be a dictionary (got {type(v).__name__}: {truncated})")

        # Validate collection names and ensure all values are Collection objects
        collection_objects = {}
        for name, value in v.items():
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
                raise ValueError(
                    f'Collection name "{name}" is invalid: must start with a letter and contain only alphanumeric characters, underscores, and hyphens (max 30 characters).'
                )
            if len(name) > 30:
                raise ValueError(
                    f'Collection name "{name}" is too long: cannot exceed 30 characters. '
                    "Collection names must start with a letter and may only contain alphanumeric characters, underscores, and hyphens."
                )

            # Convert dict to Collection object or validate existing Collection
            if isinstance(value, dict):
                logger.debug(f"Converting dict to Collection object for '{name}'")
                try:
                    collection_objects[name] = Collection(**value)
                except Exception as e:
                    raise ValueError(f"Invalid collection data for '{name}': {e}") from e
            elif isinstance(value, Collection):
                collection_objects[name] = value
            else:
                raise TypeError(
                    f"Collection '{name}' must be a dictionary or Collection object, got {type(value).__name__}"
                )

        return collection_objects

    def model_post_init(self, __context: Any) -> None:
        """Validate project configuration after initialization."""
        # Validate that collection category references exist (case-sensitive)
        category_names = set(self.categories.keys())
        if self.collections:
            for collection_name, collection in self.collections.items():
                if missing_categories := [cat for cat in collection.categories if cat not in category_names]:
                    logger.warning(
                        f"Collection '{collection_name}' references missing categories: {missing_categories}. "
                        "These categories will be ignored until they are created."
                    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values and empty lists."""
        data = self.model_dump(exclude_none=True)
        # Always include collections even if empty
        if "collections" not in data:
            data["collections"] = {}
        return {k: v for k, v in data.items() if v is not None and (k == "collections" or v not in [[], {}])}

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

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump to ensure collections are included."""
        data = super().model_dump(*args, **kwargs)
        # Always include collections in each project
        for project in data.get("projects", {}).values():
            if "collections" not in project:
                project["collections"] = {}
            # Ensure collections are properly serialized
            for collection_name, collection in project.get("collections", {}).items():
                if isinstance(collection, Collection):
                    project["collections"][collection_name] = collection.model_dump(*args, **kwargs)
                # If it's already a dict, leave it as is
        return data

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
        for name in v:
            if not name or not name.strip():
                raise ValueError("Project name cannot be empty")
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
                raise ValueError(
                    f'Project name "{name}" must start with a letter and contain only alphanumeric characters, underscores, and hyphens'
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


def _save_config_locked(config_file: Path, project_name: str, config: ProjectConfig) -> Optional[str]:
    """Internal function to save config while holding file lock.

    Returns:
        The docroot value from the saved config (for updating session state)
    """
    # Load the existing config structure or create with default docroot
    existing_config = ConfigFile(docroot=".", projects={})
    if config_file.exists():
        try:
            with open(config_file) as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict):  # Handle empty YAML files and ensure it's a dict
                    # Preserve existing docroot or default to "."
                    if "docroot" not in data or not data["docroot"]:
                        data["docroot"] = "."
                    existing_config = ConfigFile(**data)
        except yaml.YAMLError as e:
            # Handle YAML parsing errors with specific message
            logger.warning(f"Invalid YAML in config file {config_file}: {e}. Creating new configuration.")
        except (OSError, IOError) as e:
            # Handle file I/O errors
            logger.warning(f"Cannot read config file {config_file}: {e}. Creating new configuration.")
        except (ValueError, TypeError) as e:
            # Handle Pydantic validation errors
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
            # Let model_dump handle all serialization properly
            data = existing_config.model_dump(exclude_none=True)
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)
    except (OSError, IOError) as e:
        raise IOError(f"Cannot write to config file {config_file}: {e}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Cannot serialize configuration to YAML: {e}") from e

    # Return the docroot for session state update
    return existing_config.docroot


def _load_config_locked(config_file: Path, project_name: str) -> tuple[Optional[ProjectConfig], Optional[LazyPath]]:
    """Internal function to load config while holding file lock.

    Returns:
        Tuple of (ProjectConfig, docroot LazyPath) or (None, None) if not found
    """
    if not config_file.exists():
        return None, None

    try:
        with open(config_file) as f:
            data = yaml.safe_load(f)

        # Handle empty YAML files and ensure it's a dict
        if not data or not isinstance(data, dict):
            logger.warning(f"Config file {config_file} is empty or contains invalid data")
            return None, None

        # Extract docroot - default to "." if missing or empty
        docroot_str = data.get("docroot")
        if docroot_str and isinstance(docroot_str, str) and docroot_str.strip():
            docroot = LazyPath(docroot_str.strip())
        else:
            # Default to current directory if docroot is missing or empty
            docroot = LazyPath(".")

        # Load from projects structure
        if "projects" in data and project_name in data["projects"]:
            project_data = data["projects"][project_name]
            try:
                return ProjectConfig(**project_data), docroot
            except ValueError as e:
                logger.error(f"Invalid configuration for project '{project_name}': {e}")
                return None, docroot

        return None, docroot

    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in config file {config_file}: {e}")
        return None, None
    except (OSError, IOError) as e:
        logger.error(f"Cannot read config file {config_file}: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error loading config from {config_file}: {e}")
        return None, None


class ProjectConfigManager:
    """Manager for persistent project configuration."""

    def __init__(self) -> None:
        """Initialize project config manager."""
        self._config_filename: Optional[Path] = None  # Lazy initialization
        self._docroot: Optional[LazyPath] = None  # Cached docroot from config file

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
        """Save project configuration with proper file locking."""
        config_file = Path(self.get_config_filename())
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Use lock_update for proper file locking
        docroot = lock_update(config_file, _save_config_locked, project_name, config)

        # Cache the docroot after successful save (preserve new functionality)
        self._docroot = LazyPath(docroot or ".")

        # Debug output (preserve debug logging)
        logger.debug(
            f"Project config saved for project '{project_name}' with {len(config.collections) if config.collections else 0} collections."
        )

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
        project_config, docroot = lock_update(config_file, _load_config_locked, project_name_str)
        # Update cached docroot
        self._docroot = docroot
        return project_config

    @property
    def docroot(self) -> Optional[LazyPath]:
        """Get the cached docroot from the most recent load/save operation.

        Returns:
            LazyPath for docroot if available, None otherwise
        """
        return self._docroot
