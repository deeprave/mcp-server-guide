"""Server extensions for FastMCP instances."""

from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from .file_source import FileAccessor
from .session_manager import SessionManager
from .tool_decoration import ExtMcpToolDecorator


@dataclass
class ServerExtensions:
    """Extensions added to FastMCP server instances."""

    guide: ExtMcpToolDecorator
    _session_manager: SessionManager
    file_accessor: FileAccessor
    _get_file_source: Callable[[str, str], Awaitable[Any]]
    read_guide: Callable[[str], Awaitable[str]]
    read_language: Callable[[str], Awaitable[str]]
    _prompts_registered: bool = False
