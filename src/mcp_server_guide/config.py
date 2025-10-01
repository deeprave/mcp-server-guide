"""Configuration management for MCP server."""

import os
from dataclasses import dataclass
from typing import Callable, Union

from .naming import config_filename


@dataclass
class ConfigOption:
    """Configuration option with CLI, environment, and default support."""

    name: str
    cli_short: str
    cli_long: str
    env_var: str
    default: Union[str, Callable[[], str]]
    description: str


class Config:
    """Configuration manager with CLI, environment, and default support."""

    def __init__(self) -> None:
        """Initialize configuration options."""
        self.config = ConfigOption(
            name="config",
            cli_short="-c",
            cli_long="--config",
            env_var="MG_CONFIG",
            default=config_filename(),
            description="Configuration file path",
        )

        self.global_config = ConfigOption(
            name="global_config",
            cli_short="",
            cli_long="--global",
            env_var="MG_CONFIG_GLOBAL",
            default="",
            description="Use global configuration file",
        )

        self.no_global = ConfigOption(
            name="no_global",
            cli_short="",
            cli_long="--no-global",
            env_var="",
            default="",
            description="Disable global configuration file (overrides MG_CONFIG_GLOBAL)",
        )

        self.docroot = ConfigOption(
            name="docroot",
            cli_short="-d",
            cli_long="--docroot",
            env_var="MG_DOCROOT",
            default=".",
            description="Document root directory",
        )

        self.guidesdir = ConfigOption(
            name="guidesdir",
            cli_short="-g",
            cli_long="--guidesdir",
            env_var="MG_GUIDEDIR",
            default="guide/",
            description="Guidelines directory (configures 'guide' category)",
        )

        self.guide = ConfigOption(
            name="guide",
            cli_short="-G",
            cli_long="--guide",
            env_var="MG_GUIDE",
            default="guidelines",
            description="Guidelines file (configures 'guide' category)",
        )

        self.langsdir = ConfigOption(
            name="langsdir",
            cli_short="-l",
            cli_long="--langsdir",
            env_var="MG_LANGDIR",
            default="lang/",
            description="Languages directory (configures 'lang' category)",
        )

        self.lang = ConfigOption(
            name="lang",
            cli_short="-L",
            cli_long="--lang",
            env_var="MG_LANGUAGE",
            default="none",
            description="Language file (configures 'lang' category)",
        )

        self.contextdir = ConfigOption(
            name="contextdir",
            cli_short="",
            cli_long="--contextdir",
            env_var="MG_CONTEXTDIR",
            default="context/",
            description="Context directory (configures 'context' category)",
        )

        self.context = ConfigOption(
            name="context",
            cli_short="-C",
            cli_long="--context",
            env_var="MG_CONTEXT",
            default="project-context",
            description="Project context file (configures 'context' category)",
        )

        # Logging configuration
        self.log_level = ConfigOption(
            name="log_level",
            cli_short="",
            cli_long="--log-level",
            env_var="MG_LOG_LEVEL",
            default="OFF",
            description="Logging level (DEBUG, INFO, WARN, ERROR, OFF)",
        )

        self.log_file = ConfigOption(
            name="log_file",
            cli_short="",
            cli_long="--log-file",
            env_var="MG_LOG_FILE",
            default="",
            description="Log file path (empty for no file logging)",
        )

        self.log_console = ConfigOption(
            name="log_console",
            cli_short="",
            cli_long="--log-console",
            env_var="MG_LOG_CONSOLE",
            default=lambda: "true",
            description="Enable console logging (default: true unless file specified)",
        )

    def get_global_config_path(self) -> str:
        """Get platform-specific global config path."""
        from .naming import config_filename

        filename = config_filename()
        if os.name == "nt":  # Windows
            appdata = os.environ.get("APPDATA", "")
            return os.path.join(appdata, "mcp-server-guide", filename)
        else:  # Unix-like systems
            home = os.environ.get("HOME", "")
            return os.path.join(home, ".config", "mcp-server-guide", filename)

    def resolve_path(self, path: str, relative_to: str = ".") -> str:
        """Resolve a path relative to a base directory."""
        if os.path.isabs(path):
            return path
        else:
            return os.path.join(relative_to, path)

    def add_md_extension(self, path: str) -> str:
        """Add .md extension if the path doesn't have an extension."""
        if not os.path.splitext(path)[1]:
            return f"{path}.md"
        return path

    def validate_path(
        self, path: str, must_exist: bool = True, must_be_file: bool = False, must_be_dir: bool = False
    ) -> bool:
        """Validate a path exists and is of the correct type."""
        if not must_exist:
            return True

        if not os.path.exists(path):
            return False

        if must_be_file and not os.path.isfile(path):
            return False

        if must_be_dir and not os.path.isdir(path):
            return False

        return True
