"""Mock MCP server for testing."""

from typing import Dict, List, Optional


class MockResource:
    """Mock MCP resource."""

    def __init__(self, name: str, description: str = "", uri: str = ""):
        self.name = name
        self.description = description
        self.uri = uri


class MockPrompt:
    """Mock MCP prompt."""

    def __init__(self, name: str, description: str = "", arguments: Optional[List[Dict]] = None):
        self.name = name
        self.description = description
        self.arguments = arguments or []


class MockTool:
    """Mock MCP tool."""

    def __init__(self, name: str, description: str = "", input_schema: Optional[Dict] = None):
        self.name = name
        self.description = description
        self.input_schema = input_schema or {}


class MockResourceManager:
    """Mock MCP resource manager."""

    def __init__(self):
        self.resources = []
        self.prompts = []
        self.tools = []

    def list_resources(self):
        """List all resources."""
        return self.resources

    def list_prompts(self):
        """List all prompts."""
        return self.prompts

    def list_tools(self):
        """List all tools."""
        return self.tools


class MockMCP:
    """Mock MCP server for testing."""

    def __init__(self):
        self.resources = []
        self.prompts = []
        self.tools = []
        self._resource_manager = MockResourceManager()
        self._should_fail = False
        self._fail_message = "Mock failure"

    def add_resource(self, name: str, description: str = "", uri: str = ""):
        """Add a mock resource."""
        resource = MockResource(name, description, uri)
        self.resources.append(resource)
        self._resource_manager.resources.append(resource)
        return resource

    def add_prompt(self, name: str, description: str = "", arguments: Optional[List[Dict]] = None):
        """Add a mock prompt."""
        prompt = MockPrompt(name, description, arguments)
        self.prompts.append(prompt)
        self._resource_manager.prompts.append(prompt)
        return prompt

    def add_tool(self, name: str, description: str = "", input_schema: Optional[Dict] = None):
        """Add a mock tool."""
        tool = MockTool(name, description, input_schema)
        self.tools.append(tool)
        self._resource_manager.tools.append(tool)
        return tool

    def list_resources(self):
        """List all resources."""
        if self._should_fail:
            raise Exception(self._fail_message)
        return self.resources

    def list_prompts(self):
        """List all prompts."""
        if self._should_fail:
            raise Exception(self._fail_message)
        return self.prompts

    def list_tools(self):
        """List all tools."""
        if self._should_fail:
            raise Exception(self._fail_message)
        return self.tools

    def get_registered_prompts(self):
        """Get registered prompts (alias for list_prompts for compatibility)."""
        return self.list_prompts()

    def get_registered_tools(self):
        """Get registered tools (alias for list_tools for compatibility)."""
        return self.list_tools()

    def get_registered_resources(self):
        """Get registered resources (alias for list_resources for compatibility)."""
        return self.list_resources()

    def set_failure(self, should_fail: bool = True, message: str = "Mock failure"):
        """Configure mock to fail on next operation."""
        self._should_fail = should_fail
        self._fail_message = message

    def clear(self):
        """Clear all resources, prompts, and tools."""
        self.resources.clear()
        self.prompts.clear()
        self.tools.clear()
        self._resource_manager.resources.clear()
        self._resource_manager.prompts.clear()
        self._resource_manager.tools.clear()


def create_mock_mcp_with_data():
    """Create a MockMCP instance with sample data."""
    mock = MockMCP()

    # Add sample resources
    mock.add_resource("test_resource", "Test resource description", "file://test.txt")
    mock.add_resource("config_resource", "Configuration resource", "file://config.json")

    # Add sample prompts
    mock.add_prompt(
        "test_prompt",
        "Test prompt description",
        [{"name": "input", "description": "Input parameter", "required": True}],
    )
    mock.add_prompt(
        "guide_prompt", "Guide prompt", [{"name": "category", "description": "Category name", "required": False}]
    )

    # Add sample tools
    mock.add_tool("test_tool", "Test tool description", {"type": "object", "properties": {"param": {"type": "string"}}})
    mock.add_tool("search_tool", "Search tool", {"type": "object", "properties": {"query": {"type": "string"}}})

    return mock
