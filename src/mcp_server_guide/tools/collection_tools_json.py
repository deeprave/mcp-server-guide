"""JSON-based collection management tools using factory pattern."""

from .json_tool_factory import create_json_tool

guide_collections = create_json_tool("collection")
