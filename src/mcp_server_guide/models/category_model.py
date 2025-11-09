"""Category model with operation mappings."""

from types import MappingProxyType
from typing import List, Optional, ClassVar, Dict, Type
from ..operations.model_base import BaseModelOperations
from ..operations.operation_base import BaseOperation


class CategoryModel(BaseModelOperations):
    """Model representing a category with its operations."""

    operations: ClassVar[Dict[str, Type[BaseOperation]]] = {}

    @classmethod
    def get_operations(cls) -> MappingProxyType[str, Type[BaseOperation]]:
        """Get the operations mapping for this model."""
        if not cls.operations:
            # Local imports to avoid circular dependency
            from ..operations.category_ops import (
                CategoryAddOperation,
                CategoryUpdateOperation,
                CategoryRemoveOperation,
                CategoryListOperation,
                AddToCategoryOperation,
                RemoveFromCategoryOperation,
                CategoryGetContentOperation,
            )

            cls.operations = {
                "add": CategoryAddOperation,
                "update": CategoryUpdateOperation,
                "remove": CategoryRemoveOperation,
                "list": CategoryListOperation,
                "add_to": AddToCategoryOperation,
                "remove_from": RemoveFromCategoryOperation,
                "get_content": CategoryGetContentOperation,
            }
        return MappingProxyType(cls.operations)

    name: str
    dir: Optional[str] = None
    patterns: Optional[List[str]] = None
    description: Optional[str] = None
