"""Collection-specific operations."""

from typing import Any, Dict, List, Optional

from ..models.project_config import ProjectConfig
from ..tools.collection_tools import (
    add_collection,
    add_to_collection,
    get_collection_content,
    list_collections,
    remove_collection,
    remove_from_collection,
    update_collection,
)
from .operation_base import BaseOperation


class CollectionAddOperation(BaseOperation):
    """Add a new collection."""

    name: str
    categories: List[str]
    description: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await add_collection(name=self.name, categories=self.categories, description=self.description)


class CollectionUpdateOperation(BaseOperation):
    """Update an existing collection."""

    name: str
    description: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await update_collection(name=self.name, description=self.description)


class CollectionRemoveOperation(BaseOperation):
    """Remove a collection."""

    name: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await remove_collection(name=self.name)


class CollectionListOperation(BaseOperation):
    """List collections."""

    verbose: bool = False

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await list_collections(verbose=self.verbose)


class AddToCollectionOperation(BaseOperation):
    """Add categories to a collection."""

    name: str
    categories: List[str]

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await add_to_collection(name=self.name, categories=self.categories)


class RemoveFromCollectionOperation(BaseOperation):
    """Remove categories from a collection."""

    name: str
    categories: List[str]

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await remove_from_collection(name=self.name, categories=self.categories)


class GetCollectionContentOperation(BaseOperation):
    """Get collection content."""

    name: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await get_collection_content(self.name)
