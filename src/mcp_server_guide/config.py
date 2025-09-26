"""Configuration management for MCP server."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Union


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
        self.docroot = ConfigOption(
            name="docroot",
            cli_short="-d",
            cli_long="--docroot",
            env_var="MCP_DOCROOT",
            default=".",
            description="Document root directory",
        )

        self.guidesdir = ConfigOption(
            name="guidesdir",
            cli_short="-g",
            cli_long="--guidesdir",
            env_var="MCP_GUIDEDIR",
            default="aidocs/guide/",
            description="Guidelines directory",
        )

        self.guide = ConfigOption(
            name="guide",
            cli_short="-G",
            cli_long="--guide",
            env_var="MCP_GUIDE",
            default="guidelines",
            description="Guidelines file (also --guidelines)",
        )

        self.langsdir = ConfigOption(
            name="langsdir",
            cli_short="-l",
            cli_long="--langsdir",
            env_var="MCP_LANGDIR",
            default="aidocs/lang/",
            description="Languages directory",
        )

        self.lang = ConfigOption(
            name="lang",
            cli_short="-L",
            cli_long="--lang",
            env_var="MCP_LANGUAGE",
            default="",
            description="Language file (also --language)",
        )

        self.projdir = ConfigOption(
            name="projdir",
            cli_short="-p",
            cli_long="--projdir",
            env_var="MCP_PROJDIR",
            default="aidocs/project/",
            description="Project directory",
        )

        self.project = ConfigOption(
            name="project",
            cli_short="-P",
            cli_long="--project",
            env_var="MCP_PROJECT",
            default=lambda: Path.cwd().name,
            description="Project context file (also --context)",
        )

        # Logging configuration
        self.log_level = ConfigOption(
            name="log_level",
            cli_short="",
            cli_long="--log-level",
            env_var="MCP_LOG_LEVEL",
            default="OFF",
            description="Logging level (DEBUG, INFO, WARN, ERROR, OFF)",
        )

        self.log_file = ConfigOption(
            name="log_file",
            cli_short="",
            cli_long="--log-file",
            env_var="MCP_LOG_FILE",
            default="",
            description="Log file path (empty for no file logging)",
        )

        self.log_console = ConfigOption(
            name="log_console",
            cli_short="",
            cli_long="--log-console",
            env_var="MCP_LOG_CONSOLE",
            default=lambda: "true",
            description="Enable console logging (default: true unless file specified)",
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
