"""MCP tools for session-scoped project configuration."""

import asyncio
import os
from typing import Dict, Any, Optional

from mcp.server.fastmcp import Context
from pathlib import Path

from .path_resolver import LazyPath
from .project_config import ProjectConfigManager, ProjectConfig
from .models.collection import Collection
from .session import SessionState
from .logging_config import get_logger
from .models.speckit_config import SpecKitConfig


logger = get_logger()

# Global session manager instance (singleton)
_session_manager_instance: Optional["SessionManager"] = None


class SessionManager:
    """Singleton session manager with integrated project management."""

    _session_state: "SessionState"
    _config_manager: "ProjectConfigManager"
    _project_locks: Dict[str, asyncio.Lock]
    _locks_lock: asyncio.Lock
    _context_lock: asyncio.Lock
    _context_project_name: Optional[str]

    def __new__(cls) -> "SessionManager":
        # Check global instance first
        global _session_manager_instance
        if _session_manager_instance is None:
            _session_manager_instance = super().__new__(cls)
            _session_manager_instance._session_state = SessionState()
            _session_manager_instance._config_manager = ProjectConfigManager()
            _session_manager_instance._project_locks = {}
            _session_manager_instance._locks_lock = asyncio.Lock()
            _session_manager_instance._context_lock = asyncio.Lock()
            _session_manager_instance._context_project_name = None  # Resolved from client context
            logger.debug("Session manager initialized")
        return _session_manager_instance

    async def ensure_context_project_loaded(self, ctx: Optional["Context[Any, Any]"] = None) -> None:
        """Ensure project is loaded from context, handling project switches.

        Args:
            ctx: Optional FastMCP context for getting project roots
        """
        if ctx is None:
            return

        async with self._context_lock:
            try:
                # Get project roots from client context
                roots = await ctx.session.list_roots()

                if not roots:
                    logger.debug("No project roots available from client context")
                    return

                # Extract project name from first root directory
                from pathlib import Path
                from urllib.parse import urlparse

                first_root = roots[0]
                if first_root.uri.startswith("file://"):
                    try:
                        parsed = urlparse(first_root.uri)
                        project_path = Path(parsed.path)
                        current_context_name = project_path.name
                    except (ValueError, OSError) as e:
                        logger.warning(f"Failed to parse root URI {first_root.uri}: {e}")
                        return
                    logger.debug(f"Extracted project name '{current_context_name}' from context root '{project_path}'")
                else:
                    logger.warning(f"Unsupported root URI scheme: {first_root.uri}")
                    return

                # If _context_project_name is None, set it for the first time
                if self._context_project_name is None:
                    self._context_project_name = current_context_name
                    logger.debug(f"Set initial context project name: '{self._context_project_name}'")

                    # Switch to this project if it's different from current session
                    if self._session_state.project_name != current_context_name:
                        await self.switch_project(current_context_name)
                        logger.debug(f"Switched to context project: '{current_context_name}'")

                # Handle project switching if context project changes
                elif self._context_project_name != current_context_name:
                    logger.info(
                        f"Context project changed from '{self._context_project_name}' to '{current_context_name}'"
                    )
                    self._context_project_name = current_context_name
                    await self.switch_project(current_context_name)
                    logger.debug(f"Switched to new context project: '{current_context_name}'")

            except (ValueError, AttributeError, OSError) as e:
                logger.error(f"Failed to ensure context project loaded: {e}")
                # Continue with existing session state - don't fail the operation

    @classmethod
    def clear(cls) -> None:
        """Clear the session state (for testing purposes)."""
        global _session_manager_instance
        _session_manager_instance = None
        logger.debug("Session manager state cleared")

    @property
    def project_name(self) -> Optional[str]:
        """Get the current project name."""
        return self._session_state.project_name if self._session_state else None

    @property
    def session_state(self) -> SessionState:
        """Get the session state (for backward compatibility).

        Note: Direct access to session_state is deprecated. Use specific methods instead.
        """
        return self._session_state

    def get_project_config_value(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value for the current project.

        Raises AttributeError if the key is not present or its value is None and no default is provided.

        If the attribute exists but its value is None, the default is used (if provided).
        """
        if hasattr(self._session_state.project_config, key):
            value = getattr(self._session_state.project_config, key)
            if value is not None:
                return value
        if default is not None:
            return default
        raise AttributeError(f"Project config has no attribute '{key}' or its value is None")

    def get_full_project_config(self) -> ProjectConfig:
        """Get the full project configuration."""
        return self._session_state.get_project_config()

    def set_full_project_config(self, config: Dict[str, Any] | ProjectConfig) -> None:
        """Set the full project configuration."""
        if isinstance(config, dict):
            self._session_state.project_config = ProjectConfig.from_dict(config)
        elif isinstance(config, ProjectConfig):
            self._session_state.project_config = config
        else:
            raise TypeError(f"config must be a dict or ProjectConfig instance, got {type(config).__name__}")

    def reset_session_config(self, project_name: Optional[str] = None) -> None:
        """Reset the session configuration to defaults."""
        self._session_state.reset_project_config(project_name)

    def config_manager(self) -> ProjectConfigManager:
        """Get the project configuration manager."""
        return self._config_manager

    def _set_config_filename(self, filename: str | Path | LazyPath) -> None:
        """Set the configuration filename for the config manager."""
        self._config_manager.set_config_filename(filename)

    async def load_config(self, project_name: str) -> Optional[ProjectConfig]:
        return await self._config_manager.load_config(project_name)

    def set_project_name(self, project_name: str) -> None:
        if not project_name or not isinstance(project_name, str):
            raise ValueError("Project name must be a non-empty string")

        old_name = self._session_state.project_name
        if old_name != project_name:
            self._session_state.project_name = project_name
            logger.info(f"Session project name changed from '{old_name}' to '{project_name}'")

    def set_project_config(self, key: str, value: str) -> None:
        """Set configuration value for current project."""
        self._session_state.set_project_config(key, value)

    async def ensure_project_loaded(
        self, ctx: Optional["Context[Any, Any]"] = None, server: Any = None
    ) -> "ProjectConfig":
        """Ensure project is loaded, loading it if necessary.

        This handles deferred project loading after MCP handshake.

        Args:
            ctx: Optional FastMCP context for getting project roots
            server: Optional server instance for resource registration

        Returns:
            The loaded project configuration

        Raises:
            ValueError: If project name cannot be determined
        """
        # If we already have a loaded project config, return it
        if self._session_state.project_config:
            return self._session_state.project_config

        # First, ensure context project is loaded and handle switches
        await self.ensure_context_project_loaded(ctx)

        # Check if server has deferred project name
        deferred_project = getattr(server, "_deferred_project", None) if server else None

        if deferred_project:
            # Use explicit project name
            project_name = deferred_project
            logger.debug(f"Using deferred explicit project: '{project_name}'")
        else:
            # Resolve project name using session state, context, or PWD
            project_name = self.get_project_name()

        # Load the project configuration
        config = await self.get_or_create_project_config(project_name)

        # Register resources if server provided and not already registered
        if server and not getattr(server, "_resources_registered", False):
            from .resource_registry import register_resources

            await register_resources(server, config)
            server._resources_registered = True
            logger.debug("Resources registered after deferred project loading")

        return config

    def get_project_name(self) -> str:
        """Get the current project name.

        Returns project name from session state, context resolution, or PWD fallback.

        Raises:
            ValueError: If no project name can be determined
        """
        # If project_name is set in session state, return it
        if self._session_state.project_name:
            logger.debug(f"Returning session state project_name: {self._session_state.project_name}")
            return self._session_state.project_name

        # Try context-resolved project name (set by ensure_context_project_loaded)
        if self._context_project_name:
            logger.debug(f"Using context-resolved project: '{self._context_project_name}'")
            return self._context_project_name

        # Fallback to PWD environment variable
        from pathlib import Path

        pwd = os.getenv("PWD")
        if not pwd:
            logger.error("No project name available from session, context, or PWD environment variable")
            raise ValueError(
                "Cannot determine project name: no session state, context resolution, or PWD environment variable available"
            )

        project_name = Path(pwd).name
        logger.debug(f"Using PWD fallback for project: '{project_name}' (from {pwd})")
        return project_name

    def reset_project_config(self, project_name: Optional[str] = None) -> None:
        """Reset current project to defaults."""
        from .project_config import ProjectConfig

        self._session_state.reset_project_config(project_name)
        categories = self.default_categories()
        self._session_state.project_config = ProjectConfig(categories=categories)

    async def save_session(self) -> None:
        """Save session state to config file."""
        # Ensure we have a project name (will detect from PWD if not set)
        project_name = self.get_project_name()
        if not project_name:
            return

        # Load existing config from file (if it exists)
        from .models.category import Category

        if existing_config := await self._config_manager.load_config(project_name):
            # Merge session state changes into existing config
            session_config = self._session_state.get_project_config()

            # Convert categories to objects
            category_objects = {
                cat_name: (
                    cat_data
                    if isinstance(cat_data, Category) or not isinstance(cat_data, dict)
                    else Category(**cat_data)
                )
                for cat_name, cat_data in session_config.categories.items()
            }
            # Replace categories completely instead of updating to handle removals
            existing_config.categories = category_objects

            # Convert collections to objects
            collection_objects = {}
            for coll_name, coll_data in session_config.collections.items():
                if isinstance(coll_data, Collection):
                    collection_objects[coll_name] = coll_data
                elif isinstance(coll_data, dict):
                    logger.debug(f"Converting dict to Collection object for '{coll_name}' in session")
                    try:
                        collection_objects[coll_name] = Collection(**coll_data)
                    except Exception as e:
                        logger.error("Failed to instantiate Collection for '%s': %s. Data: %r", coll_name, e, coll_data)
                        raise ValueError(f"Invalid collection data for '{coll_name}': {e}") from e
                else:
                    logger.error(
                        "Invalid collection data type for '%s': expected dict or Collection, got %s",
                        coll_name,
                        type(coll_data),
                    )
                    raise ValueError(
                        f"Invalid collection data type for '{coll_name}': expected dict or Collection, got {type(coll_data)}"
                    )
            # Replace collections completely to handle removals
            existing_config.collections = collection_objects
            project_config = existing_config
        else:
            # No existing config, use session state directly
            project_config = self._session_state.get_project_config()

        # Save using config manager with project name as key
        await self._config_manager.save_config(project_name, project_config)

    async def safe_save_session(self) -> None:
        """Auto-save session state with error handling that won't propagate exceptions."""
        try:
            await self.save_session()
            logger.debug("Auto-saved session")
        except Exception as e:
            logger.warning(f"Auto-save failed: {e}")
            # Don't raise - operations should succeed even if save fails

    async def get_or_create_project_config(self, project: str) -> ProjectConfig:
        """Get project config and auto-save if project was newly created."""

        # Get or create project-specific lock to prevent race conditions
        async with self._locks_lock:
            if project not in self._project_locks:
                self._project_locks[project] = asyncio.Lock()
            project_lock = self._project_locks[project]

        # Use project-specific lock for atomic operations
        async with project_lock:
            # Check if project is already current BEFORE calling get_project_config
            # (since get_project_config creates the project if it doesn't exist)
            project_is_current = self._session_state.project_name == project
            logger.debug(f"Project '{project}' is already current: {project_is_current}")

            if project_is_current:
                logger.debug(f"Project '{project}' is already current")
            else:
                # fetch existing or initialise a new project with built-in categories
                try:
                    await self.switch_project(project)
                except Exception as e:
                    logger.warning(f"Failed to initialize project '{project}': {e}")

            return self._session_state.get_project_config()

    async def switch_project(self, project_name: str) -> ProjectConfig:
        """Manually switch project context."""
        if not project_name or not isinstance(project_name, str):
            raise ValueError("Project name must be a non-empty string")

        if project_name != self.project_name:
            project_config = await self.load_config(project_name)
            if project_config:
                # Load existing config into session state
                self._session_state.set_project_name(project_name)
                self._session_state.project_config = project_config
                logger.info(f"Switched to existing project '{project_name}' with loaded configuration")
                return project_config

            # create a new project with default categories
            self.reset_project_config(project_name)
            self._session_state.set_project_name(project_name)  # Ensure project name is set
            logger.info(f"Switched to new project '{project_name}' with default configuration")
        else:
            logger.info(f"Switched to same project '{project_name}'")

        return self._session_state.get_project_config()

    @staticmethod
    def default_categories() -> Dict[str, Any]:
        """Create the four default categories for new projects."""
        from .models.category import Category

        return {
            "guide": Category(
                dir="guide/", patterns=["guidelines"], description="Project guidelines and development rules", url=None
            ),
            "lang": Category(dir="lang/", patterns=["none"], description="Language-specific guidelines", url=None),
            "context": Category(
                dir="context/",
                patterns=["project-context"],
                description="Context information for AI assistants",
                url=None,
            ),
        }

    @property
    def docroot(self) -> Optional[LazyPath]:
        return self._config_manager.docroot or LazyPath(".")

    async def get_speckit_config(self) -> Optional["SpecKitConfig"]:
        """Get SpecKit configuration - delegates to service."""
        return await self._config_manager.get_speckit_config()

    async def set_speckit_config(self, speckit_config: "SpecKitConfig") -> None:
        """Set SpecKit configuration - delegates to service."""
        await self._config_manager.set_speckit_config(speckit_config)

    async def is_speckit_enabled(self) -> bool:
        """Check if SpecKit is enabled - delegates to service."""
        speckit_config = await self.get_speckit_config()
        return speckit_config is not None and speckit_config.enabled


async def set_project_config(key: str, value: str) -> Dict[str, Any]:
    """Set configuration value for current project."""
    session_manager = SessionManager()
    try:
        current_project = session_manager.get_project_name()
        session_manager.set_project_config(key, value)
        return {"success": True, "message": f"Set {key} to '{value}' for project {current_project}"}
    except ValueError as e:
        return {"success": False, "error": str(e)}


async def get_project_config() -> Dict[str, Any]:
    """Get current project's configuration."""
    session_manager = SessionManager()

    try:
        current_project = session_manager.get_project_name()
        config = await session_manager.get_or_create_project_config(current_project)
        return {"success": True, "project": current_project, "config": config.to_dict()}
    except ValueError as e:
        return {"success": False, "error": str(e)}


async def reset_project_config() -> Dict[str, Any]:
    """Reset current project to defaults."""
    session_manager = SessionManager()
    current_project = session_manager.get_project_name()

    session_manager.reset_project_config(current_project)

    return {"success": True, "message": f"Reset project {current_project} to defaults"}


async def switch_project(project_name: str) -> Dict[str, Any]:
    """Manually switch project context."""
    if not project_name or not isinstance(project_name, str):
        raise ValueError("Project name must be a non-empty string")

    session_manager = SessionManager()
    await session_manager.switch_project(project_name)

    return {"success": True, "message": f"Switched to project {project_name}"}


# Export singleton instance getter for backward compatibility
def session_manager() -> SessionManager:
    """Get the singleton SessionManager instance."""
    return SessionManager()
