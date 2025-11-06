"""Schema tools for dynamic schema generation and validation."""

from typing import Dict, Any
from ..operations.schema_generator import get_all_schemas, get_schema_for_context, generate_tool_description


async def guide_get_schemas() -> Dict[str, Any]:
    """Get all instruction schemas for AI agent visibility.

    Returns complete schema definitions showing valid actions and arguments
    for each context (category, collection, document, content, config).
    """
    try:
        schemas = get_all_schemas()
        return {"success": True, "schemas": schemas, "total_contexts": len(schemas)}
    except Exception as e:
        return {"success": False, "error": f"Failed to get schemas: {str(e)}"}


async def guide_get_schema(context: str) -> Dict[str, Any]:
    """Get schema for specific context.

    Args:
        context: The context to get schema for (category, collection, document, content, config)
    """
    try:
        schema = get_schema_for_context(context)
        if not schema:
            return {"success": False, "error": f"No schema found for context: {context}"}

        return {"success": True, "context": context, "schema": schema}
    except Exception as e:
        return {"success": False, "error": f"Failed to get schema for {context}: {str(e)}"}


async def generate_description(entity_type: str) -> Dict[str, Any]:
    """Generate tool description for entity type."""
    try:
        description = generate_tool_description(entity_type)
        return {"success": True, "entity_type": entity_type, "description": description}
    except Exception as e:
        return {"success": False, "error": f"Failed to generate description for {entity_type}: {str(e)}"}


__all__ = ["guide_get_schemas", "guide_get_schema", "generate_description"]
