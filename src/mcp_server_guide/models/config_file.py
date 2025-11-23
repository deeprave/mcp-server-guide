"""Configuration file model."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .project_config import ProjectConfig
from .speckit_config import SpecKitConfig


def get_default_docroot() -> str:
    """Get the default docroot path."""
    from ..config_paths import get_default_docroot

    return str(get_default_docroot())


class ConfigFile(BaseModel):
    """Complete configuration file with global settings and projects."""

    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True,  # Validate on assignment
    )

    docroot: Optional[str] = Field(default_factory=get_default_docroot, description="Global project root directory")
    projects: Dict[str, ProjectConfig] = Field(default_factory=dict, description="Project configurations")
    speckit: Optional[SpecKitConfig] = Field(None, description="SpecKit global configuration")

    @field_validator("projects")
    @classmethod
    def validate_projects(cls, v: Dict[str, ProjectConfig]) -> Dict[str, ProjectConfig]:
        """Validate project names."""
        for project_name in v:
            if not project_name or not project_name.strip():
                raise ValueError("Project name cannot be empty")
        return v

    @field_validator("docroot")
    @classmethod
    def validate_docroot(cls, v: Optional[str]) -> str:
        """Validate and normalize docroot."""
        if v is None:
            return get_default_docroot()

        # Strip whitespace
        v = v.strip()

        # If empty or whitespace only, default to proper default
        if not v:
            return get_default_docroot()

        # Check for path traversal
        if ".." in v:
            raise ValueError("Global document root cannot contain path traversal sequences")

        return v

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override model_dump to ensure collections are included."""
        data = super().model_dump(*args, **kwargs)
        # Always include collections in each project
        for project_name, project_config in data.get("projects", {}).items():
            if "collections" not in project_config:
                project_config["collections"] = {}
        return data
