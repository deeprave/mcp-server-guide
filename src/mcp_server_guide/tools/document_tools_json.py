"""JSON-based document management tools using Pydantic operations."""

from typing import Dict, Any
from ..operations.base import execute_json_operation


async def guide_documents(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle document operations via JSON instructions."""
    return await execute_json_operation("document", data)
