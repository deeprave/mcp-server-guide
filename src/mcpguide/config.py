"""Configuration module for MCP server."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any
import click


@dataclass
class ConfigOption:
    """Configuration option with CLI and environment variable support."""
    name: str
    cli_short: str
    cli_long: str
    env_var: str
    default: str | Callable[[], str]
    is_file: bool
    description: str


class Config:
    """Configuration container with all MCP server options."""

    def __init__(self) -> None:
        self.docroot = ConfigOption(
            name="docroot",
            cli_short="-d",
            cli_long="--docroot",
            env_var="MCP_DOCROOT",
            default=".",
            is_file=False,
            description="Document root directory"
        )

        self.guidesdir = ConfigOption(
            name="guidesdir",
            cli_short="-g",
            cli_long="--guidesdir",
            env_var="MCP_GUIDEDIR",
            default="guide/",
            is_file=False,
            description="Guidelines directory"
        )

        self.guide = ConfigOption(
            name="guide",
            cli_short="-G",
            cli_long="--guide",
            env_var="MCP_GUIDE",
            default="guidelines",
            is_file=True,
            description="Guidelines file (also --guidelines)"
        )

        self.langdir = ConfigOption(
            name="langdir",
            cli_short="-l",
            cli_long="--langs",
            env_var="MCP_LANGDIR",
            default="lang/",
            is_file=False,
            description="Languages directory"
        )

        self.language = ConfigOption(
            name="language",
            cli_short="-L",
            cli_long="--lang",
            env_var="MCP_LANGUAGE",
            default="",
            is_file=True,
            description="Language file (also --language)"
        )

        self.projdir = ConfigOption(
            name="projdir",
            cli_short="-p",
            cli_long="--projdir",
            env_var="MCP_PROJDIR",
            default="project/",
            is_file=False,
            description="Project directory"
        )

        self.project = ConfigOption(
            name="project",
            cli_short="-P",
            cli_long="--project",
            env_var="MCP_PROJECT",
            default=lambda: Path.cwd().name,
            is_file=True,
            description="Project context file (also --context)"
        )


def create_click_command(config: Config) -> click.Command:
    """Create a click command from configuration options."""

    # Get all config options dynamically
    options = []
    for attr_name in dir(config):
        if not attr_name.startswith('_'):
            attr = getattr(config, attr_name)
            if isinstance(attr, ConfigOption):
                options.append(attr)

    @click.command()
    def main(**kwargs: Any) -> None:
        """MCP server with configurable paths."""
        pass

    # Add options dynamically
    for option in options:
        default_val = option.default() if callable(option.default) else option.default
        main = click.option(
            option.cli_short, option.cli_long,
            envvar=option.env_var,
            default=default_val,
            help=option.description
        )(main)

    return main
