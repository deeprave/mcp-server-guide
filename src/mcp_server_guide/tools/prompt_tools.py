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


__all__ = ["list_prompts"]
