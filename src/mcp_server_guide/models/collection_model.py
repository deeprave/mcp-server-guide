"""Collection model with operation mappings."""

from types import MappingProxyType
from typing import ClassVar, Dict, List, Optional, Type

from ..operations.model_base import BaseModelOperations
from ..operations.operation_base import BaseOperation


class CollectionModel(BaseModelOperations):
    """Model representing a collection with its operations."""

    operations: ClassVar[Dict[str, Type[BaseOperation]]] = {}

    @classmethod
    def get_operations(cls) -> MappingProxyType[str, Type[BaseOperation]]:
        """Get the operations mapping for this model."""
        if not cls.operations:
            # Local imports to avoid circular dependency
            from ..operations.collection_ops import (
                AddToCollectionOperation,
                CollectionAddOperation,
                CollectionListOperation,
                CollectionRemoveOperation,
                CollectionUpdateOperation,
                GetCollectionContentOperation,
                RemoveFromCollectionOperation,
            )

            cls.operations = {
                "add": CollectionAddOperation,
                "update": CollectionUpdateOperation,
                "remove": CollectionRemoveOperation,
                "list": CollectionListOperation,
                "add_to": AddToCollectionOperation,
                "remove_from": RemoveFromCollectionOperation,
                "get_content": GetCollectionContentOperation,
            }
        return MappingProxyType(cls.operations)

    name: str
    categories: Optional[List[str]] = None
    description: Optional[str] = None
