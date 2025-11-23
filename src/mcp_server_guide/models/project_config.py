"""Project configuration models."""

import re
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..logging_config import get_logger
from .category import Category
from .collection import Collection

logger = get_logger(__name__)


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
                truncated = f"{truncated[:100]}..."
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
