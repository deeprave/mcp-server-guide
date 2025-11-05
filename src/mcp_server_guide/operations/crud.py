"""Generic CRUD operations for all entity types."""

from abc import abstractmethod
from typing import Optional, Dict, Any
from .base import BaseOperation, T
from ..models.project_config import ProjectConfig


class AddOperation(BaseOperation[T]):
    """Generic add operation."""

    name: str
    description: Optional[str] = None

    @abstractmethod
    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Execute the add operation."""
        pass


class UpdateOperation(BaseOperation[T]):
    """Generic update operation."""

    name: str
    description: Optional[str] = None

    @abstractmethod
    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Execute the update operation."""
        pass


class RemoveOperation(BaseOperation[T]):
    """Generic remove operation."""

    name: str

    @abstractmethod
    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Execute the remove operation."""
        pass


class ListOperation(BaseOperation[T]):
    """Generic list operation."""

    verbose: bool = False

    @abstractmethod
    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Execute the list operation."""
        pass
