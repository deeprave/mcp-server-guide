"""JSON-based category management tools using factory pattern."""

from .json_tool_factory import create_json_tool

guide_categories = create_json_tool("category")
