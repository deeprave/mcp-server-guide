"""Category-specific operations."""

from typing import Any, Dict, List, Optional

from ..models.project_config import ProjectConfig
from ..tools.category_tools import (
    add_category,
    add_to_category,
    get_category_content,
    list_categories,
    remove_category,
    remove_from_category,
    update_category,
)
from .operation_base import BaseOperation


class CategoryAddOperation(BaseOperation):
    """Add a new category."""

    name: str
    dir: str
    patterns: List[str]
    description: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await add_category(name=self.name, dir=self.dir, patterns=self.patterns, description=self.description)


class CategoryUpdateOperation(BaseOperation):
    """Update an existing category."""

    name: str
    dir: Optional[str] = None
    patterns: Optional[List[str]] = None
    description: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await update_category(name=self.name, dir=self.dir, patterns=self.patterns, description=self.description)


class CategoryRemoveOperation(BaseOperation):
    """Remove a category."""

    name: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await remove_category(name=self.name)


class CategoryListOperation(BaseOperation):
    """List categories."""

    verbose: bool = False

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await list_categories(verbose=self.verbose)


class AddToCategoryOperation(BaseOperation):
    """Add patterns to a category."""

    name: str
    patterns: List[str]

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await add_to_category(name=self.name, patterns=self.patterns)


class RemoveFromCategoryOperation(BaseOperation):
    """Remove patterns from a category."""

    name: str
    patterns: List[str]

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await remove_from_category(name=self.name, patterns=self.patterns)


class CategoryGetContentOperation(BaseOperation):
    """Get content from a category."""

    name: str
    file: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await get_category_content(name=self.name, file=self.file)
