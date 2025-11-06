"""Server extensions for FastMCP instances."""

from dataclasses import dataclass

from .file_source import FileAccessor
from .session_manager import SessionManager


@dataclass
class ServerExtensions:
    """Extensions added to FastMCP server instances."""

    _session_manager: SessionManager  # Session and project configuration management
    file_accessor: FileAccessor  # File reading and caching functionality
    _prompts_registered: bool = False
