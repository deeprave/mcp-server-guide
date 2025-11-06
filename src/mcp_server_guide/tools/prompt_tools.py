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
    from ..server import get_current_server_sync

    server = get_current_server_sync()
    if server is None:
        return {"success": False, "error": "No server instance available", "prompts": [], "total_prompts": 0}

    # Access the prompt manager from the current server instance
    prompts = server.get_registered_prompts()

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
        from ..server import get_current_server_sync

        server = get_current_server_sync()
        if server is None:
            return {"success": False, "error": "No server instance available", "resources": [], "total_resources": 0}

        # Use the server's method to get registered resources
        resources = server.get_registered_resources()

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
