"""Factory for creating JSON tool functions to eliminate duplication."""

from typing import Dict, Any, Callable, Awaitable
from ..operations.base import execute_json_operation


def create_json_tool(entity_type: str) -> Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]:
    """Create a JSON tool function for the specified entity type.

    Args:
        entity_type: The entity type (e.g., 'category', 'collection')

    Returns:
        Async function that handles JSON operations for the entity type
    """

    async def json_tool(data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle operations via JSON instructions."""
        return await execute_json_operation(entity_type, data)

    json_tool.__doc__ = f"Handle {entity_type} operations via JSON instructions."
    return json_tool
