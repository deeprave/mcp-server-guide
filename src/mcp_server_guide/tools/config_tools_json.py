"""JSON-based config management tools using factory pattern."""

from .json_tool_factory import create_json_tool

guide_config = create_json_tool("config")
