"""Server extensions for FastMCP instances."""

import asyncio
from dataclasses import dataclass, field
from typing import Any

from .file_source import FileAccessor
from .session_manager import SessionManager


@dataclass
class ServerExtensions:
    """Extensions added to FastMCP server instances."""

    _session_manager: SessionManager  # Session and project configuration management
    file_accessor: FileAccessor  # File reading and caching functionality
    _prompts_registered: bool = False
    _tools_registered: bool = field(default=False)
    _registration_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def register_tools_once(self, server: Any, registration_func: Any) -> None:
        """Register tools exactly once with thread safety."""
        async with self._registration_lock:
            if self._tools_registered:
                return  # Early return if already registered

            # Perform tool registration (sync function)
            registration_func(server)

            self._tools_registered = True

    async def cleanup(self) -> None:
        """Clean up extension resources."""
        try:
            # Clean up session manager if it has cleanup method
            if hasattr(self._session_manager, "cleanup"):
                await self._session_manager.cleanup()

            # Clean up file accessor if it has cleanup method
            if hasattr(self.file_accessor, "cleanup"):
                await self.file_accessor.cleanup()

        except Exception as e:
            # Import logger here to avoid circular imports
            from .logging_config import get_logger

            logger = get_logger()
            logger.error(f"Error during extensions cleanup: {e}")
