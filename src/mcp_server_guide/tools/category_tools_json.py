"""JSON-based category management tools using Pydantic operations."""

from typing import Dict, Any
from ..operations.base import execute_json_operation


async def guide_categories(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle category operations via JSON instructions."""
    return await execute_json_operation("category", data)
