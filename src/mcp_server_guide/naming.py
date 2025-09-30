"""Centralized naming for MCP server components."""

# Version constant for centralized version management
MCP_GUIDE_VERSION = "1.0"

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


def config_filename() -> str:
    """Return the configuration filename."""
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
