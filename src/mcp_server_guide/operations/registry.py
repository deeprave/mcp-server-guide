"""Operation registry for dynamic operation discovery."""

from typing import Dict, Type, Any
from .base import BaseOperation
from .category_ops import (
    CategoryAddOperation,
    CategoryUpdateOperation,
    CategoryRemoveOperation,
    CategoryListOperation,
    AddToCategoryOperation,
    RemoveFromCategoryOperation,
)
from .collection_ops import (
    CollectionAddOperation,
    CollectionUpdateOperation,
    CollectionRemoveOperation,
    CollectionListOperation,
    AddToCollectionOperation,
    RemoveFromCollectionOperation,
    GetCollectionContentOperation,
)
from .document_ops import (
    DocumentCreateOperation,
    DocumentUpdateOperation,
    DocumentDeleteOperation,
    DocumentListOperation,
)
from .content_ops import GetContentOperation, SearchContentOperation, GetFileContentOperation
from .config_ops import (
    GetCurrentProjectOperation,
    GetProjectConfigOperation,
    SetProjectConfigOperation,
    SetProjectConfigValuesOperation,
    SwitchProjectOperation,
)


OPERATION_REGISTRY: Dict[str, Dict[str, Type[BaseOperation]]] = {
    "category": {
        "add": CategoryAddOperation,
        "update": CategoryUpdateOperation,
        "remove": CategoryRemoveOperation,
        "list": CategoryListOperation,
        "add_to": AddToCategoryOperation,
        "remove_from": RemoveFromCategoryOperation,
    },
    "collection": {
        "add": CollectionAddOperation,
        "update": CollectionUpdateOperation,
        "remove": CollectionRemoveOperation,
        "list": CollectionListOperation,
        "add_to": AddToCollectionOperation,
        "remove_from": RemoveFromCollectionOperation,
        "get_content": GetCollectionContentOperation,
    },
    "document": {
        "create": DocumentCreateOperation,
        "update": DocumentUpdateOperation,
        "delete": DocumentDeleteOperation,
        "list": DocumentListOperation,
    },
    "content": {
        "get": GetContentOperation,
        "search": SearchContentOperation,
        "get_file": GetFileContentOperation,
    },
    "config": {
        "get_current_project": GetCurrentProjectOperation,
        "get_project_config": GetProjectConfigOperation,
        "set_project_config": SetProjectConfigOperation,
        "set_project_config_values": SetProjectConfigValuesOperation,
        "switch_project": SwitchProjectOperation,
    },
}


def get_operation_class(entity_type: str, action: str) -> Type[BaseOperation]:
    """Get operation class for entity type and action."""
    entity_ops = OPERATION_REGISTRY.get(entity_type)
    if not entity_ops:
        raise ValueError(f"Unknown entity type: {entity_type}")

    operation_class = entity_ops.get(action)
    if not operation_class:
        raise ValueError(f"Unknown action '{action}' for context '{entity_type}'")

    return operation_class


def get_operation_schema(entity_type: str, action: str) -> Dict[str, Any]:
    """Get JSON schema for an operation."""
    operation_class = get_operation_class(entity_type, action)
    return operation_class.model_json_schema()
