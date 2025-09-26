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
    contextdir: Optional[str] = None
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

    def start(self) -> None:
        """Start watching for changes."""
        self.observer.schedule(self.handler, str(self.config_path.parent), recursive=False)
        self.observer.start()

    def stop(self) -> None:
        """Stop watching for changes."""
        self.observer.stop()
        self.observer.join()


class ConfigChangeHandler(FileSystemEventHandler):
    """Handle configuration file changes."""

    def __init__(self, config_path: Path, callback: Callable[[ProjectConfig], None]):
        self.config_path = config_path
        self.callback = callback

    def on_modified(self, event: Any) -> None:
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

    CONFIG_FILENAME = ".mcp-server-guide.config.json"

    def save_config(self, project_path: Path, config: ProjectConfig) -> None:
        """Save project configuration to file, preserving existing projects."""
        config_file = project_path / self.CONFIG_FILENAME

        # Load existing config structure
        existing_data: Dict[str, Any] = {"projects": {}}
        if config_file.exists():
            try:
                with open(config_file) as f:
                    existing_data = json.load(f)
                    if "projects" not in existing_data:
                        existing_data["projects"] = {}
            except (json.JSONDecodeError, OSError):
                # Handle corrupted files
                existing_data = {"projects": {}}

        # Remove current_project field if it exists (Issue 012)
        existing_data.pop("current_project", None)

        # Update the specific project
        project_dict = config.to_dict()
        project_name = project_dict.pop("project")  # Remove project name from data
        existing_data["projects"][project_name] = project_dict

        # Save updated config
        with open(config_file, "w") as f:
            json.dump(existing_data, f, indent=2)

    def load_config(self, project_path: Path, project_name: Optional[str] = None) -> Optional[ProjectConfig]:
        """Load project configuration from file with migration support."""
        config_file = project_path / self.CONFIG_FILENAME

        if not config_file.exists():
            return None

        try:
            with open(config_file) as f:
                data = json.load(f)

            # Handle migration from old format
            if project_name and "projects" in data and project_name in data["projects"]:
                project_data = data["projects"][project_name].copy()

                # Migrate projdir to contextdir
                if "projdir" in project_data and "contextdir" not in project_data:
                    project_data["contextdir"] = project_data.pop("projdir")

                # Ensure project name is set
                project_data["project"] = project_name

                return ProjectConfig.from_dict(project_data)

            # Handle direct project config (legacy single-project format)
            if "project" in data:
                # Migrate projdir to contextdir
                if "projdir" in data and "contextdir" not in data:
                    data["contextdir"] = data.pop("projdir")
                return ProjectConfig.from_dict(data)

            return None

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

    def save_session_config(self, project_path: Path, session: Any, project_name: str) -> None:
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

    def save_full_session_state(
        self, project_path: Path, session: Any, config_filename: str = ".mcp-server-guide.config.json"
    ) -> None:
        """Save complete session state including all projects."""
        config_file = project_path / config_filename

        session_data = {"current_project": session.current_project, "projects": session.session_state.projects.copy()}

        import json

        with open(config_file, "w") as f:
            json.dump(session_data, f, indent=2)

    def load_full_session_state(
        self, project_path: Path, session: Any, config_filename: str = ".mcp-server-guide.config.json"
    ) -> bool:
        """Load complete session state including all projects."""
        config_file = project_path / config_filename

        if not config_file.exists():
            return False

        try:
            import json

            with open(config_file) as f:
                session_data = json.load(f)

            # Restore session state
            if "projects" in session_data:
                session.session_state.projects = session_data["projects"]

            if "current_project" in session_data:
                session.set_current_project(session_data["current_project"])

            return True
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            return False
