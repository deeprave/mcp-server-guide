"""Content model with operation mappings."""

from types import MappingProxyType
from typing import Optional, ClassVar, Dict, Type
from ..operations.model_base import BaseModelOperations
from ..operations.operation_base import BaseOperation


class ContentModel(BaseModelOperations):
    """Model representing content with its operations."""

    operations: ClassVar[Dict[str, Type[BaseOperation]]] = {}

    @classmethod
    def get_operations(cls) -> MappingProxyType[str, Type[BaseOperation]]:
        """Get the operations mapping for this model."""
        if not cls.operations:
            # Local imports to avoid circular dependency
            from ..operations.content_ops import (
                GetContentOperation,
                SearchContentOperation,
                GetFileContentOperation,
            )

            cls.operations = {
                "get": GetContentOperation,
                "search": SearchContentOperation,
                "get_file": GetFileContentOperation,
            }
        return MappingProxyType(cls.operations)

    category_or_collection: Optional[str] = None
    document: Optional[str] = None
    query: Optional[str] = None
    path: Optional[str] = None
    project: Optional[str] = None
