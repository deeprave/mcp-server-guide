"""MCP server for developer guidelines and project rules."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Developer Guide MCP")

defaults = {
    "guide": "./guide/",
    "project": "./project/",
    "lang": "./lang/",
}
