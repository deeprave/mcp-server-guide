"""MCP tools for session-scoped project configuration."""

import asyncio
import os
from typing import Dict, Any, Optional
from pathlib import Path
from .session import SessionState
from .logging_config import get_logger
from .validation import validate_config_key, ConfigValidationError

logger = get_logger()


class SessionManager:
    """Singleton session manager with integrated project management."""

    _instance: Optional["SessionManager"] = None
    session_state: SessionState
    _project_locks: Dict[str, asyncio.Lock]
    _locks_lock: asyncio.Lock
    _current_project: Optional[str]

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session_state = SessionState()
            cls._instance._current_project = None
            cls._instance._project_locks = {}
            cls._instance._locks_lock = asyncio.Lock()
            logger.debug("Session manager initialized")
        return cls._instance

    async def get_current_project(self) -> Optional[str]:
        """Get current project name."""
        # If _current_project is set, return it
        if self._current_project is not None:
            return self._current_project

        # Use PWD environment variable as fallback
        from pathlib import Path

        pwd = os.getenv("PWD")
        if pwd:
            project_name = Path(pwd).name
            logger.debug(f"Using PWD basename as project: '{project_name}' (from {pwd})")
            return project_name

        # If PWD not available, this is an error condition
        logger.error("PWD environment variable not set - cannot determine project")
        return None

    async def set_current_project(self, project_name: str) -> None:
        """Set current project name in session memory.

        Args:
            project_name: Name of the project to set as current

        Raises:
            ValueError: If project name is empty
        """
        if not project_name or not isinstance(project_name, str):
            raise ValueError("Project name must be a non-empty string")

        old_project = await self.get_current_project()
        self._current_project = project_name
        logger.info(f"Session project changed from '{old_project}' to '{project_name}'")

    async def save_to_file(self, config_file_path: str) -> None:
        """Save session state to config file, preserving existing data."""
        import json
        from pathlib import Path
        import aiofiles

        config_file = Path(config_file_path)

        # Load existing config or create new structure
        existing_config = {}
        if config_file.exists():
            try:
                async with aiofiles.open(config_file, "r", encoding="utf-8") as f:
                    content = await f.read()
                    existing_config = json.loads(content)
            except (json.JSONDecodeError, OSError) as e:
                # Handle corrupted files by backing up and starting fresh
                logger.warning(f"Config file corrupted or unreadable, backing up and starting fresh: {e}")
                backup_file = config_file.with_suffix(".json.backup")
                if config_file.exists():
                    config_file.rename(backup_file)
                    logger.info(f"Backed up corrupted config to {backup_file}")
                existing_config = {}

        # Ensure projects structure exists
        if "projects" not in existing_config:
            existing_config["projects"] = {}

        # Update with current session data (preserve existing projects)
        for project_name, project_config in self.session_state.projects.items():
            if project_name not in existing_config["projects"]:
                existing_config["projects"][project_name] = {}

            # Update only the fields that have been set, preserve others
            existing_config["projects"][project_name].update(project_config)

        # Remove current_project field if it exists (Issue 012)
        existing_config.pop("current_project", None)

        # Write updated config
        async with aiofiles.open(config_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(existing_config, indent=2))

    async def get_current_project_safe(self) -> str:
        """Get current project with error handling for None case."""
        project = await self.get_current_project()
        if project is None:
            logger.error("Cannot determine client working directory - MCP server cannot function")
            raise ValueError("Working directory not set. Use set_directory() first.")
        return project

    async def get_or_create_project_config(self, project: str) -> Dict[str, Any]:
        """Get project config and auto-save if project was newly created."""
        from .naming import config_filename

        # Get or create project-specific lock to prevent race conditions
        async with self._locks_lock:
            if project not in self._project_locks:
                self._project_locks[project] = asyncio.Lock()
            project_lock = self._project_locks[project]

        # Use project-specific lock for atomic operations
        async with project_lock:
            # Check if project exists before getting config
            existing_project_config = self.session_state.projects.get(project)
            project_existed = existing_project_config is not None

            # Get config (may create project in memory)
            config = await self.session_state.get_project_config(project)

            # Auto-save if project was just created
            if not project_existed:
                try:
                    await self.save_to_file(config_filename())
                    logger.debug(f"Auto-saved newly created project '{project}'")
                except Exception as e:
                    logger.warning(f"Auto-save failed for new project '{project}': {e}")

            return config

    async def load_project_from_path(self, project_path: Any) -> None:
        """Load project configuration from path."""
        logger.debug(f"Loading project configuration from {project_path}")
        from .project_config import ProjectConfigManager

        manager = ProjectConfigManager()
        config = manager.load_config(project_path)
        if config:
            await self.set_current_project(config.project)
            # Load config into session state
            for key, value in config.to_dict().items():
                if key != "project":
                    await self.session_state.set_project_config(config.project, key, value)

    async def get_effective_config(self, project_name: str) -> Dict[str, Any]:
        """Get effective configuration combining file and session overrides with resolved paths."""
        config = await self.session_state.get_project_config(project_name)

        # Resolve docroot to absolute path
        docroot = config.get("docroot", ".")
        if not Path(docroot).is_absolute():
            # Resolve relative paths to absolute
            config["docroot"] = str(Path(docroot).resolve())

        return config


# Global session manager instance
_session_manager = SessionManager()


async def set_project_config(key: str, value: str) -> Dict[str, Any]:
    """Set configuration value for current project."""
    session_manager = SessionManager()

    # Validate the key and value before setting
    try:
        validate_config_key(key, value)
    except ConfigValidationError as e:
        return {"success": False, "error": str(e), "errors": e.errors}

    try:
        current_project = await session_manager.get_current_project_safe()
        await session_manager.session_state.set_project_config(current_project, key, value)
        return {"success": True, "message": f"Set {key} to '{value}' for project {current_project}"}
    except ValueError as e:
        return {"success": False, "error": str(e)}


async def get_project_config() -> Dict[str, Any]:
    """Get current project's configuration."""
    session_manager = SessionManager()

    try:
        current_project = await session_manager.get_current_project_safe()
        config = await session_manager.session_state.get_project_config(current_project)
        return {"success": True, "project": current_project, "config": config}
    except ValueError as e:
        return {"success": False, "error": str(e)}


async def list_project_configs() -> Dict[str, Any]:
    """List all project configurations."""
    session_manager = SessionManager()

    projects = {}
    for project_name in session_manager.session_state.projects:
        projects[project_name] = await session_manager.session_state.get_project_config(project_name)

    return {"success": True, "projects": projects}


async def reset_project_config() -> Dict[str, Any]:
    """Reset current project to defaults."""
    session_manager = SessionManager()

    current_project = await session_manager.get_current_project()
    if current_project in session_manager.session_state.projects:
        del session_manager.session_state.projects[current_project]

    return {"success": True, "message": f"Reset project {current_project} to defaults"}


async def switch_project(project_name: str) -> Dict[str, Any]:
    """Manually switch project context."""
    if not project_name or not isinstance(project_name, str):
        raise ValueError("Project name must be a non-empty string")

    session_manager = SessionManager()
    await session_manager.set_current_project(project_name)

    return {"success": True, "message": f"Switched to project {project_name}"}


async def set_local_file(key: str, local_path: str) -> Dict[str, Any]:
    """Set config to use local file."""
    return await set_project_config(key, local_path)


_session_state = _session_manager.session_state
_current_project = None
