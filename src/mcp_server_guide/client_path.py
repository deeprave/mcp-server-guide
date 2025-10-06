"""Client Path - Static interface for MCP client working directory access."""

import asyncio
import os
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from mcp.server.session import ServerSession


class ClientPath:
    """Static manager for client working directory access.

    This class provides a centralized interface for accessing the client working directory.
    The directory is determined using these methods in priority order:

    1. MCP roots/list protocol (optional) - if client declares roots capability
    2. PWD environment variable - standard Unix practice, set by client's shell/process
    3. Server process CWD via os.getcwd() - fallback (may not match client directory)

    Note: PWD and os.getcwd() are different:
    - PWD: Client's working directory (where client is running)
    - os.getcwd(): Server's working directory (set via --directory flag when launching server)

    CRITICAL: Client directory must be initialized during server startup via initialize()
    before any other methods can be used.
    """

    _primary_root: Optional[Path] = None
    _initialized: bool = False
    _init_lock: Optional[asyncio.Lock] = None

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if ClientPath has been initialized."""
        return cls._initialized

    @classmethod
    def get_init_lock(cls) -> asyncio.Lock:
        """Get the initialization lock, creating it if needed."""
        if cls._init_lock is None:
            cls._init_lock = asyncio.Lock()
        return cls._init_lock

    @classmethod
    async def initialize(cls, session: "ServerSession") -> None:
        """Initialize client working directory during server startup.

        Attempts to get working directory via:
        1. MCP roots capability (if client supports it)
        2. PWD environment variable (standard Unix practice - client's working directory)
        3. Server process CWD via os.getcwd() (fallback)

        Args:
            session: Active MCP session with client context

        Raises:
            RuntimeError: If client working directory cannot be determined
        """
        from .logging_config import get_logger

        logger = get_logger()

        # Try MCP roots/list first (optional capability)
        if session.client_params and session.client_params.capabilities.roots:
            try:
                result = await session.list_roots()
                if result and result.roots:
                    cls._primary_root = cls._parse_file_uri(str(result.roots[0].uri))
                    logger.info(f"Initialized client directory via MCP roots protocol: {cls._primary_root}")
                    cls._initialized = True
                    return
            except Exception as e:
                logger.warning(f"MCP roots/list failed (will try fallback): {e}")

        # Check PWD environment variable (set by client's shell/process)
        if "PWD" in os.environ:
            client_dir = Path(os.environ["PWD"]).resolve()
            logger.info(f"Initialized client directory from PWD environment variable: {client_dir}")
            cls._primary_root = client_dir
            cls._initialized = True
            return

        # Fallback: Use server process working directory
        try:
            cls._primary_root = Path(os.getcwd()).resolve()
            logger.warning(
                f"Using server process CWD as fallback (may not match client directory): {cls._primary_root}"
            )
            cls._initialized = True
        except Exception as e:
            error_msg = f"Cannot determine client working directory: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    @classmethod
    def get_primary_root(cls) -> Optional[Path]:
        """Get primary client working directory.

        Returns:
            Primary client working directory or None if not initialized
        """
        if not cls._initialized:
            return None

        return cls._primary_root

    @classmethod
    def list_roots(cls) -> List[Path]:
        """Get all client working directories.

        Returns:
            List containing the primary working directory, or empty list if not initialized
        """
        if not cls._initialized:
            return []

        if cls._primary_root:
            return [cls._primary_root]

        return []

    @staticmethod
    def _parse_file_uri(uri: str) -> Path:
        """Parse file:// URI to Path object.

        Args:
            uri: File URI (must start with file://) - can be string or FileUrl type

        Returns:
            Path object

        Raises:
            ValueError: If URI doesn't start with file://
        """
        # Convert to string if it's a FileUrl type
        uri_str = str(uri)

        if not uri_str.startswith("file://"):
            raise ValueError("URI must start with file://")

        parsed = urlparse(uri_str)
        return Path(parsed.path)
