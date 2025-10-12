"""Configuration management for MCP server."""

import os
from dataclasses import dataclass
from typing import Callable, Union


@dataclass
class ConfigOption:
    """Configuration option with CLI, environment, and default support."""

    name: str
    cli_short: str
    cli_long: str
    env_var: str
    default: Union[str, bool, Callable[[], str], None]
    description: str
    group: str = "other"


class Config:
    """Configuration manager with CLI, environment, and default support."""

    def __init__(self) -> None:
        """Initialize configuration options."""
        self.config = ConfigOption(
            name="config",
            cli_short="-c",
            cli_long="--config",
            env_var="MG_CONFIG",
            default=None,
            description="specify config file path",
            group="config",
        )

        self.docroot = ConfigOption(
            name="docroot",
            cli_short="-d",
            cli_long="--docroot",
            env_var="MG_DOCROOT",
            default=".",
            description="server document root (absolute path)",
            group="docroot",
        )

        self.guide = ConfigOption(
            name="guide",
            cli_short="-g",
            cli_long="--guide",
            env_var="MG_GUIDE",
            default="guidelines",
            description="*guide file patterns",
            group="content",
        )

        self.guidesdir = ConfigOption(
            name="guidesdir",
            cli_short="",
            cli_long="--guidesdir",
            env_var="MG_GUIDEDIR",
            default="guide/",
            description="**guide directory path",
            group="content",
        )

        self.lang = ConfigOption(
            name="lang",
            cli_short="-l",
            cli_long="--lang",
            env_var="MG_LANGUAGE",
            default="none",
            description="*language file patterns",
            group="content",
        )

        self.langsdir = ConfigOption(
            name="langsdir",
            cli_short="",
            cli_long="--langsdir",
            env_var="MG_LANGDIR",
            default="lang/",
            description="**language directory path",
            group="content",
        )

        self.context = ConfigOption(
            name="context",
            cli_short="",
            cli_long="--context",
            env_var="MG_CONTEXT",
            default="project-context",
            description="*context file patterns",
            group="content",
        )

        self.contextdir = ConfigOption(
            name="contextdir",
            cli_short="",
            cli_long="--contextdir",
            env_var="MG_CONTEXTDIR",
            default="context/",
            description="**context directory path",
            group="content",
        )

        # Logging configuration
        self.log_level = ConfigOption(
            name="log_level",
            cli_short="",
            cli_long="--log-level",
            env_var="MG_LOG_LEVEL",
            default="OFF",
            description="Logging level (DEBUG, INFO, WARN, ERROR, OFF)",
            group="logging",
        )

        self.log_file = ConfigOption(
            name="log_file",
            cli_short="",
            cli_long="--log-file",
            env_var="MG_LOG_FILE",
            default="",
            description="Log file path (empty for no file logging)",
            group="logging",
        )

        self.log_console = ConfigOption(
            name="log_console",
            cli_short="",
            cli_long="--log-console",
            env_var="MG_LOG_CONSOLE",
            default=lambda: "true",
            description="Enable console logging (default: true unless file specified)",
            group="logging",
        )

        self.log_json = ConfigOption(
            name="log_json",
            cli_short="",
            cli_long="--log-json",
            env_var="MG_LOG_JSON",
            default=False,
            description="Enable JSON structured logging to file (console remains text format)",
            group="logging",
        )

        self.version = ConfigOption(
            name="version",
            cli_short="",
            cli_long="--version",
            env_var="",
            default="",
            description="Show version and exit",
            group="other",
        )

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
