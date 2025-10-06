"""MCP Rules Server for developer guidelines and project rules."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("mcp-server-guide")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
