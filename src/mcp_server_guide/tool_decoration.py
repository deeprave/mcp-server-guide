"""Tool decoration and logging for MCP server."""

import functools
import inspect
from typing import Any, Callable, Optional, cast
from .logging_config import get_logger

logger = get_logger()


def log_tool_usage(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log tool usage."""
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            tool_name = func.__name__
            logger.info(f"Tool called: {tool_name}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Tool {tool_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {str(e)}")
                raise

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            tool_name = func.__name__
            logger.info(f"Tool called: {tool_name}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Tool {tool_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {str(e)}")
                raise

        return sync_wrapper  # type: ignore[return-value]


def get_tool_prefix() -> str:
    """Get the tool prefix for MCP tools."""
    import os

    return os.getenv("MCP_TOOL_PREFIX", "guide")


class ExtMcpToolDecorator:
    """Extended MCP tool decorator with prefix handling."""

    def __init__(self, server: Any, prefix: Optional[str] = None):
        self.server = server
        self.default_prefix = prefix or f"{get_tool_prefix()}_"
        self.prefix = self.default_prefix

    def tool(self, name: Optional[str] = None, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Tool decorator that handles prefix addition."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Use function name if no name provided
            tool_name = name or func.__name__

            # Extract prefix from kwargs if provided
            prefix = kwargs.pop("prefix", None)

            # Use provided prefix or default
            active_prefix = prefix if prefix is not None else self.prefix

            # Add prefix if not empty
            final_name = f"{active_prefix}{tool_name}" if active_prefix else tool_name
            # Build final kwargs
            final_kwargs = {"name": final_name}
            final_kwargs.update(kwargs)

            return cast(Callable[..., Any], self.server.tool(**final_kwargs)(func))

        return decorator
