from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


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

        # Collections must have at least one category to be meaningful
        if not v:
            raise ValueError("Collection must contain at least one category")

        # Validate category name format
        from ..utils.validation import is_valid_name

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
        # Inline validation to avoid circular imports
        if not isinstance(v, str):
            raise ValueError("Description must be a string")
        return v.strip() if v else ""
