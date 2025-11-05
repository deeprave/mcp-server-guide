"""Schema visibility tools for AI agents."""

from typing import Dict, Any
from ..operations.registry import OPERATION_REGISTRY


async def guide_get_schemas() -> Dict[str, Any]:
    """Get all instruction schemas for AI agent visibility.

    Returns complete schema definitions showing valid actions and arguments
    for each context (category, collection, document, content, config).
    """
    schemas: Dict[str, Any] = {}
    for entity_type in OPERATION_REGISTRY:
        schemas[entity_type] = {}
        for action in OPERATION_REGISTRY[entity_type]:
            operation_class = OPERATION_REGISTRY[entity_type][action]
            schema = operation_class.model_json_schema()
            schemas[entity_type][action] = list(schema.get("properties", {}).keys())

    return {
        "success": True,
        "schemas": schemas,
        "usage": {
            "description": "Schema definitions for JSON instruction validation",
            "format": "context -> action -> valid_arguments_set",
            "example": {
                "category": {
                    "add": ["name", "dir", "patterns", "description"],
                    "update": ["name", "description", "dir", "patterns"],
                    "remove": ["name"],
                }
            },
        },
    }


async def guide_get_schema(context: str) -> Dict[str, Any]:
    """Get schema for specific context.

    Args:
        context: The context to get schema for (category, collection, document, content, config)
    """
    if context not in OPERATION_REGISTRY:
        return {"success": False, "error": f"Unknown context: {context}"}

    schema = {}
    for action in OPERATION_REGISTRY[context]:
        operation_class = OPERATION_REGISTRY[context][action]
        operation_schema = operation_class.model_json_schema()
        schema[action] = list(operation_schema.get("properties", {}).keys())

    return {"success": True, "context": context, "schema": schema, "actions": list(schema.keys())}
