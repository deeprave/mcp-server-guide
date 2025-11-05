"""JSON-based config management tools using Pydantic operations."""

from typing import Dict, Any
from ..operations.base import execute_json_operation


async def guide_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle config operations via JSON instructions."""
    return await execute_json_operation("config", data)
