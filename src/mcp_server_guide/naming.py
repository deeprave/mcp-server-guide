"""Centralized naming for MCP server components."""

import importlib.metadata

# Version constant for centralized version management
try:
    MCP_GUIDE_VERSION = importlib.metadata.version("mcp-server-guide")
except importlib.metadata.PackageNotFoundError:
    MCP_GUIDE_VERSION = "unknown"

# Module-level constant for backward compatibility
CONFIG_FILENAME = ".mcp-server-guide.config.json"


def mcp_name() -> str:
    """Return the MCP server name used across all components.

    This provides a single point of control for the server name,
    making it easy to rebrand or rename in the future.

    Returns:
        The MCP server name string
    """
    return "mcp-server-guide"


def config_filename(is_global: bool = False) -> str:
    """Return the configuration filename."""
    if is_global:
        return f"{mcp_name()}.config.json"
    return f".{mcp_name()}.config.json"


def current_filename() -> str:
    """Return the current project filename."""
    return f".{mcp_name()}.current"


def cache_directory_name() -> str:
    """Return the cache directory name."""
    return mcp_name()


def logger_name() -> str:
    """Return the logger name."""
    return mcp_name()


def user_agent() -> str:
    """Return the HTTP User-Agent string."""
    return f"{mcp_name()}/{MCP_GUIDE_VERSION}"
