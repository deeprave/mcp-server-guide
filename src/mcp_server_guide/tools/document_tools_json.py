"""JSON-based document management tools using factory pattern."""

from .json_tool_factory import create_json_tool

guide_documents = create_json_tool("document")
