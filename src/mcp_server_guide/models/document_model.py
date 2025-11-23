"""Document model with operation mappings."""

from types import MappingProxyType
from typing import ClassVar, Dict, Optional, Type

from ..operations.model_base import BaseModelOperations
from ..operations.operation_base import BaseOperation


class DocumentModel(BaseModelOperations):
    """Model representing a document with its operations."""

    operations: ClassVar[Dict[str, Type[BaseOperation]]] = {}

    @classmethod
    def get_operations(cls) -> MappingProxyType[str, Type[BaseOperation]]:
        """Get the operations mapping for this model."""
        if not cls.operations:
            # Local imports to avoid circular dependency
            from ..operations.document_ops import (
                DocumentCreateOperation,
                DocumentDeleteOperation,
                DocumentListOperation,
                DocumentUpdateOperation,
            )

            cls.operations = {
                "create": DocumentCreateOperation,
                "update": DocumentUpdateOperation,
                "delete": DocumentDeleteOperation,
                "list": DocumentListOperation,
            }
        return MappingProxyType(cls.operations)

    name: str
    category_dir: str
    content: Optional[str] = None
    mime_type: Optional[str] = None
    source_type: Optional[str] = None
