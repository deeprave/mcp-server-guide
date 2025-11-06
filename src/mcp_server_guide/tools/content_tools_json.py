"""JSON-based content management tools using factory pattern."""

from .json_tool_factory import create_json_tool

guide_content = create_json_tool("content")
