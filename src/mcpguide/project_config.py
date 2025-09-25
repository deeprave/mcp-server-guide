"""Persistent project configuration (Issue 004)."""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


@dataclass
class ProjectConfig:
    """Project configuration data."""

    project: str
    guide: Optional[str] = None
    language: Optional[str] = None
    docroot: Optional[str] = None
    guidesdir: Optional[str] = None
    langdir: Optional[str] = None
    projdir: Optional[str] = None
    tools: Optional[List[str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values and empty lists."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None and v != []}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        """Create from dictionary."""
        return cls(**data)


class ConfigFileWatcher:
    """File watcher for configuration changes."""

    def __init__(self, config_path: Path, callback: Callable[[ProjectConfig], None]):
        self.config_path = config_path
        self.callback = callback
        self.observer = Observer()
        self.handler = ConfigChangeHandler(config_path, callback)

    def start(self):
        """Start watching for changes."""
        self.observer.schedule(self.handler, str(self.config_path.parent), recursive=False)
        self.observer.start()

    def stop(self):
        """Stop watching for changes."""
        self.observer.stop()
        self.observer.join()


class ConfigChangeHandler(FileSystemEventHandler):
    """Handle configuration file changes."""

    def __init__(self, config_path: Path, callback: Callable[[ProjectConfig], None]):
        self.config_path = config_path
        self.callback = callback

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and Path(event.src_path) == self.config_path:
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                config = ProjectConfig.from_dict(data)
                self.callback(config)
            except (json.JSONDecodeError, FileNotFoundError):
                # Ignore invalid or missing files
                pass


class ProjectConfigManager:
    """Manager for persistent project configuration."""

    CONFIG_FILENAME = ".mcpguide.config.json"

    def save_config(self, project_path: Path, config: ProjectConfig) -> None:
        """Save project configuration to file."""
        config_file = project_path / self.CONFIG_FILENAME

        with open(config_file, "w") as f:
            json.dump(config.to_dict(), f, indent=2)

    def load_config(self, project_path: Path) -> Optional[ProjectConfig]:
        """Load project configuration from file."""
        config_file = project_path / self.CONFIG_FILENAME

        if not config_file.exists():
            return None

        try:
            with open(config_file) as f:
                data = json.load(f)
            return ProjectConfig.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def detect_project_root(self, start_path: Path) -> Optional[Path]:
        """Detect project root by finding config file."""
        current_path = start_path.resolve()

        # Search up the directory tree
        while current_path != current_path.parent:
            config_file = current_path / self.CONFIG_FILENAME
            if config_file.exists():
                return current_path
            current_path = current_path.parent

        return None

    def watch_config(self, project_path: Path, callback: Callable[[ProjectConfig], None]) -> ConfigFileWatcher:
        """Watch configuration file for changes."""
        config_file = project_path / self.CONFIG_FILENAME
        watcher = ConfigFileWatcher(config_file, callback)
        watcher.start()
        return watcher

    def save_session_config(self, project_path: Path, session, project_name: str) -> None:
        """Save session configuration to persistent file."""
        # Get session config for the specific project
        session_config = session.session_state.get_project_config(project_name)

        # Create ProjectConfig from session data, ensuring project name is preserved
        config_data = {"project": project_name}
        for key, value in session_config.items():
            if key != "project":  # Don't override the project name
                config_data[key] = value

        config = ProjectConfig.from_dict(config_data)
        self.save_config(project_path, config)
