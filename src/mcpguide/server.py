"""MCP server for developer guidelines and project rules."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Developer Guide MCP")

defaults = {
    "guide": "./guide/",
    "project": "./project/",
    "lang": "./lang/",
}


def create_server_with_config(config: dict[str, str]) -> FastMCP:
    """Create MCP server instance with configuration."""
    server = FastMCP(name="Developer Guide MCP")
    # TODO: Configure server with resolved config values
    return server
