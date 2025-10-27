"""MCP tools for session-scoped project configuration."""

import asyncio
import os
from typing import Dict, Any, Optional
from pathlib import Path

from .path_resolver import LazyPath
from .project_config import ProjectConfigManager, ProjectConfig, Category, Collection
from .session import SessionState
from .logging_config import get_logger


logger = get_logger()


class SessionManager:
    """Singleton session manager with integrated project management."""

    _instance: Optional["SessionManager"] = None
    _session_state: SessionState
    _project_locks: Dict[str, asyncio.Lock]
    _locks_lock: asyncio.Lock
    _config_manager: ProjectConfigManager

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._session_state = SessionState()
            cls._instance._config_manager = ProjectConfigManager()
            cls._instance._project_locks = {}
            cls._instance._locks_lock = asyncio.Lock()
            logger.debug("Session manager initialized")
        return cls._instance

    @classmethod
    def clear(cls) -> None:
        """Clear the session state (for testing purposes)."""
        cls._instance = None
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
        return self._config_manager.load_config(project_name)

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

    def get_project_name(self) -> str:
        """Get the current project name.

        Raises:
            ValueError: If PWD environment variable is not set
        """
        # If project_name is set, return it
        if self._session_state.project_name:
            return self._session_state.project_name

        # Use PWD environment variable - REQUIRED
        from pathlib import Path

        pwd = os.getenv("PWD")
        if not pwd:
            logger.error("PWD environment variable is not set - MCP server cannot function")
            raise ValueError("PWD environment variable not set. MCP server requires PWD to determine project context.")

        project_name = Path(pwd).name
        logger.debug(f"Using PWD basename as project: '{project_name}' (from {pwd})")
        return project_name

    def reset_project_config(self, project_name: Optional[str] = None) -> None:
        """Reset current project to defaults."""
        from .project_config import ProjectConfig

        self._session_state.reset_project_config(project_name)
        self._session_state.project_config = ProjectConfig(categories=self.builtin_categories())

    async def save_session(self) -> None:
        """Save session state to config file."""
        # Ensure we have a project name (will detect from PWD if not set)
        project_name = self.get_project_name()
        if not project_name:
            return

        # Load existing config from file (if it exists)
        from .project_config import Category

        if existing_config := self._config_manager.load_config(project_name):
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
        self._config_manager.save_config(project_name, project_config)

    async def get_or_create_project_config(self, project: str) -> ProjectConfig:
        """Get project config and auto-save if project was newly created."""

        # Get or create project-specific lock to prevent race conditions
        async with self._locks_lock:
            if project not in self._project_locks:
                self._project_locks[project] = asyncio.Lock()
            project_lock = self._project_locks[project]

        # Use project-specific lock for atomic operations
        async with project_lock:
            # Check if project exists BEFORE calling get_project_config
            # (since get_project_config creates the project if it doesn't exist)
            project_is_current = self._session_state.project_name == project
            logger.debug(f"Project '{project}' existed: {project_is_current}")

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
    def builtin_categories() -> Dict[str, Any]:
        """Create built-in categories with default values."""
        return {
            "guide": Category(
                url=None,
                dir="guide/",
                patterns=["guidelines"],
                description="Development guidelines",
            ),
            "lang": Category(
                url=None,
                dir="lang/",
                patterns=["none"],
                description="Language-specific guidelines",
            ),
            "context": Category(
                url=None,
                dir="context/",
                patterns=["project-context"],
                description="Project-specific guidelines",
            ),
        }

    @property
    def docroot(self) -> Optional[LazyPath]:
        return self._config_manager.docroot or LazyPath(".")


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
