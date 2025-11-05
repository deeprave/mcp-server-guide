"""JSON-based content access tools using Pydantic operations."""

from typing import Dict, Any
from ..operations.base import execute_json_operation


async def guide_content(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle content operations via JSON instructions."""
    return await execute_json_operation("content", data)
