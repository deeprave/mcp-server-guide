"""JSON-based collection management tools using Pydantic operations."""

from typing import Dict, Any
from ..operations.base import execute_json_operation


async def guide_collections(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle collection operations via JSON instructions."""
    return await execute_json_operation("collection", data)
