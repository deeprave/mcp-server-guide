"""Prompt discovery tools."""

from typing import Dict, Any, List


async def list_prompts() -> Dict[str, Any]:
    """List all available prompts registered with the MCP server.

    Returns:
        Dict containing:
        - success: bool
        - prompts: List of prompt metadata dicts
        - total_prompts: int count of prompts
    """
    from ..server import mcp

    if mcp is None:
        return {"success": False, "error": "MCP server not initialized", "prompts": []}

    # Access the prompt manager from the global mcp instance
    prompts = mcp._prompt_manager.list_prompts()

    # Convert prompt objects to dicts with metadata
    prompt_list: List[Dict[str, Any]] = []
    for prompt in prompts:
        prompt_dict = {
            "name": prompt.name,
            "description": prompt.description or "",
            "arguments": [
                {
                    "name": arg.name,
                    "description": arg.description or "",
                    "required": arg.required,
                }
                for arg in (prompt.arguments or [])
            ],
        }
        prompt_list.append(prompt_dict)

    return {
        "success": True,
        "prompts": prompt_list,
        "total_prompts": len(prompt_list),
    }


async def list_resources() -> Dict[str, Any]:
    """List all available resources registered with the MCP server.

    Returns:
        Dict containing:
        - success: bool
        - resources: List of resource metadata dicts
        - total_resources: int count of resources
    """
    try:
        from ..server import mcp

        if mcp is None:
            return {"success": False, "error": "MCP server not initialized", "resources": []}

        # Try to access resource manager safely
        resources_result: Any = None
        resources: Any = None
        if hasattr(mcp, "list_resources"):
            # Use public method if available (may be async)
            resources_result = mcp.list_resources()
            if hasattr(resources_result, "__await__"):
                resources = await resources_result
            else:
                resources = resources_result
        elif hasattr(mcp, "_resource_manager") and hasattr(mcp._resource_manager, "list_resources"):
            # Fallback to private access with safety check
            resources_result = mcp._resource_manager.list_resources()
            if hasattr(resources_result, "__await__"):
                resources = await resources_result
            else:
                resources = resources_result
        else:
            # Graceful fallback when resource manager is not accessible
            return {
                "success": False,
                "error": "Resource listing not available in current MCP version",
                "resources": [],
                "total_resources": 0,
            }

        # Convert resource objects to dicts with metadata
        resource_list: List[Dict[str, Any]] = []
        for resource in resources:
            try:
                resource_dict = {
                    "uri": getattr(resource, "uri", ""),
                    "name": getattr(resource, "name", ""),
                    "description": getattr(resource, "description", "") or "",
                    "mime_type": getattr(resource, "mime_type", None),
                }
                resource_list.append(resource_dict)
            except Exception:
                # Skip malformed resources but continue processing
                continue

        return {
            "success": True,
            "resources": resource_list,
            "total_resources": len(resource_list),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list resources: {str(e)}",
            "resources": [],
            "total_resources": 0,
        }


__all__ = ["list_prompts", "list_resources"]
