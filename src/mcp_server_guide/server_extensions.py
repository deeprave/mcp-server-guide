"""Server extensions for FastMCP instances."""

from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from .file_source import FileAccessor
from .session_manager import SessionManager


@dataclass
class ServerExtensions:
    """Extensions added to FastMCP server instances."""

    _session_manager: SessionManager  # Session and project configuration management
    file_accessor: FileAccessor  # File reading and caching functionality
    _get_file_source: Callable[[str, str], Awaitable[Any]]  # Get file source for config key and project
    read_guide: Callable[[str], Awaitable[str]]  # Read guide content for project context
    read_language: Callable[[str], Awaitable[str]]  # Read language content for project context
    _prompts_registered: bool = False
