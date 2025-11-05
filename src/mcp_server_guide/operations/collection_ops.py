"""Collection-specific operations."""

from typing import List, Dict, Any
from .crud import AddOperation, UpdateOperation, RemoveOperation, ListOperation
from .base import BaseOperation
from ..models.project_config import ProjectConfig
from ..tools.collection_tools import (
    add_collection,
    update_collection,
    remove_collection,
    list_collections,
    add_to_collection,
    remove_from_collection,
    get_collection_content,
)


class CollectionAddOperation(AddOperation):
    """Add a new collection."""

    categories: List[str]

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await add_collection(name=self.name, categories=self.categories, description=self.description)


class CollectionUpdateOperation(UpdateOperation):
    """Update an existing collection."""

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await update_collection(name=self.name, description=self.description)


class CollectionRemoveOperation(RemoveOperation):
    """Remove a collection."""

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await remove_collection(name=self.name)


class CollectionListOperation(ListOperation):
    """List collections."""

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
        return await get_collection_content(name=self.name)
