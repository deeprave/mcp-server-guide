"""Persistent project configuration (Issue 004)."""

import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

from .file_lock import lock_update
from .logging_config import get_logger
from .path_resolver import LazyPath
from .models.project_config import ProjectConfig
from .models.config_file import ConfigFile
from .models.speckit_config import SpecKitConfig

__all__ = ["ProjectConfig", "ProjectConfigManager"]

logger = get_logger(__name__)

# Configure YAML to handle datetime objects automatically
yaml.add_representer(datetime, lambda dumper, data: dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat()))


class ProjectConfigManager:
    """Manager for persistent project configuration."""

    def __init__(self) -> None:
        """Initialize project config manager."""
        self._config_filename: Optional[Path] = None  # Lazy initialization
        self._docroot: Optional[LazyPath] = None  # Cached docroot from config file

    def set_config_filename(self, filename: str | LazyPath | Path | None) -> None:
        """Set the config filename explicitly."""
        if filename:
            # Convert LazyPath to Path if needed
            if isinstance(filename, LazyPath):
                self._config_filename = Path(str(filename)).resolve()
            else:
                self._config_filename = Path(filename).resolve()

    def get_config_filename(self) -> Path:
        """Get config filename - returns full global path."""
        if self._config_filename is None:
            self._config_filename = _get_global_config_path()
        return self._config_filename

    def save_config(self, project_name: str, config: ProjectConfig) -> None:
        """Save project configuration with proper file locking."""
        config_file = Path(self.get_config_filename())
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Use lock_update for proper file locking
        docroot = lock_update(config_file, _save_config_locked, project_name, config)

        # Cache the docroot after successful save (preserve new functionality)
        self._docroot = LazyPath(docroot or ".")

        # Debug output (preserve debug logging)
        logger.debug(
            f"Project config saved for project '{project_name}' with {len(config.collections) if config.collections else 0} collections."
        )

    def load_config(self, project_name: str) -> Optional[ProjectConfig]:
        """Load project configuration from file.

        Args:
            project_name: Name of the project to load (must not be empty)

        Returns:
            ProjectConfig if found, None otherwise
        """
        # Convert to string if Path object
        project_name_str = project_name or ""
        if not project_name_str or not project_name_str.strip():
            raise ValueError("Project name cannot be empty")

        config_file = Path(self.get_config_filename())

        # Use file locking to ensure thread-safe reads
        project_config, docroot = lock_update(config_file, _load_config_locked, project_name_str)
        # Update cached docroot
        self._docroot = docroot
        return project_config

    @property
    def docroot(self) -> Optional[LazyPath]:
        """Get the cached docroot from the most recent load/save operation.

        Returns:
            LazyPath for docroot if available, None otherwise
        """
        return self._docroot

    def get_speckit_config(self) -> Optional["SpecKitConfig"]:
        """Get SpecKit configuration from global config file."""
        from .file_lock import lock_update

        config_file = self.get_config_filename()

        def _load_speckit(file_path: Path) -> Optional["SpecKitConfig"]:
            if not file_path.exists():
                return None

            try:
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                config_data = ConfigFile(**data)
                return config_data.speckit
            except Exception:
                return None

        return lock_update(config_file, _load_speckit)

    def set_speckit_config(self, speckit_config: "SpecKitConfig") -> None:
        """Set SpecKit configuration in global config file."""
        from .file_lock import lock_update

        config_file = self.get_config_filename()

        def _save_speckit(file_path: Path, config: "SpecKitConfig") -> None:
            # Load existing config or create new
            if file_path.exists():
                try:
                    with open(file_path, "r") as f:
                        data = yaml.safe_load(f) or {}
                except yaml.YAMLError:
                    data = {}
            else:
                data = {}

            # Create ConfigFile instance
            try:
                config_data = ConfigFile(**data)
            except Exception:
                config_data = ConfigFile(docroot=".", projects={}, speckit=None)

            # Update speckit config
            config_data.speckit = config

            # Save back to file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                yaml.dump(config_data.model_dump(exclude_none=True), f, default_flow_style=False)

        lock_update(config_file, _save_speckit, speckit_config)


def _get_global_config_path() -> Path:
    """Get the default global config file path."""
    import os

    # Use XDG_CONFIG_HOME if available, otherwise ~/.config
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        config_dir = Path(config_home)
    else:
        config_dir = Path.home() / ".config"

    return config_dir / "mcp-server-guide" / "config.yaml"


def _save_config_locked(config_file: Path, project_name: str, config: ProjectConfig) -> str:
    """Save project configuration with file locking (internal function)."""
    try:
        # Load existing config file or create new one
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    data = yaml.safe_load(f) or {}
            except yaml.YAMLError:
                # If existing file is corrupted, start fresh
                data = {}
        else:
            data = {}

        # Create ConfigFile instance
        try:
            config_data = ConfigFile(**data)
        except Exception:
            # If existing data is invalid, start fresh
            config_data = ConfigFile(
                projects={}, docroot="~/", speckit=SpecKitConfig(enabled=False, url="", version="")
            )

        # Update the specific project
        config_data.projects[project_name] = config

        # Save back to file
        try:
            with open(config_file, "w") as f:
                yaml.dump(config_data.model_dump(), f, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError as e:
            raise ValueError("Cannot serialize configuration to YAML") from e

        # Return docroot
        return config_data.docroot or "."
    except ValueError:
        # Re-raise ValueError (from YAML serialization)
        raise
    except Exception:
        # Re-raise other exceptions
        raise


def _load_config_locked(config_file: Path, project_name: str) -> tuple[Optional[ProjectConfig], Optional[LazyPath]]:
    """Load project configuration with file locking (internal function)."""
    logger = get_logger(__name__)

    try:
        if not config_file.exists():
            return None, None

        try:
            with open(config_file, "r") as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML config for {project_name}: {e}")
            return None, None
        except (OSError, IOError) as e:
            logger.warning(f"Failed to read config file for {project_name}: {e}")
            return None, None

        try:
            config_data = ConfigFile(**data)
        except Exception as e:
            logger.warning(f"Invalid config data for {project_name}: {e}")
            return None, None

        project_config = config_data.projects.get(project_name)
        docroot = LazyPath(config_data.docroot) if config_data.docroot else None

        return project_config, docroot
    except Exception as e:
        logger.error(f"Unexpected error loading config for {project_name}: {e}")
        return None, None
