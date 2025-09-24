"""Configuration module for MCP server."""

import os
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
            description="Document root directory",
        )

        self.guidesdir = ConfigOption(
            name="guidesdir",
            cli_short="-g",
            cli_long="--guidesdir",
            env_var="MCP_GUIDEDIR",
            default="guide/",
            is_file=False,
            description="Guidelines directory",
        )

        self.guide = ConfigOption(
            name="guide",
            cli_short="-G",
            cli_long="--guide",
            env_var="MCP_GUIDE",
            default="guidelines",
            is_file=True,
            description="Guidelines file (also --guidelines)",
        )

        self.langdir = ConfigOption(
            name="langdir",
            cli_short="-l",
            cli_long="--langsdir",
            env_var="MCP_LANGDIR",
            default="lang/",
            is_file=False,
            description="Languages directory",
        )

        self.language = ConfigOption(
            name="language",
            cli_short="-L",
            cli_long="--lang",
            env_var="MCP_LANGUAGE",
            default="",
            is_file=True,
            description="Language file (also --language)",
        )

        self.projdir = ConfigOption(
            name="projdir",
            cli_short="-p",
            cli_long="--projdir",
            env_var="MCP_PROJDIR",
            default="project/",
            is_file=False,
            description="Project directory",
        )

        self.project = ConfigOption(
            name="project",
            cli_short="-P",
            cli_long="--project",
            env_var="MCP_PROJECT",
            default=get_project_name,
            is_file=True,
            description="Project context file (also --context)",
        )


def create_click_command(config: Config) -> click.Command:
    """Create a click command from configuration options."""

    # Get all config options dynamically
    options = []
    for attr_name in dir(config):
        if not attr_name.startswith("_"):
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
            option.cli_short, option.cli_long, envvar=option.env_var, default=default_val, help=option.description
        )(main)

    return main


def resolve_env_vars(config: Config) -> dict[str, str]:
    """Resolve environment variables with fallbacks to defaults."""
    resolved = {}

    # Get all config options dynamically
    for attr_name in dir(config):
        if not attr_name.startswith("_"):
            attr = getattr(config, attr_name)
            if isinstance(attr, ConfigOption):
                # Check environment variable first, then use default
                env_value = os.environ.get(attr.env_var)
                if env_value is not None:
                    resolved[attr.name] = env_value
                else:
                    default_val = attr.default() if callable(attr.default) else attr.default
                    resolved[attr.name] = default_val

    return resolved


def resolve_path(path: str, docroot: str, is_file: bool) -> str:
    """Resolve path relative to docroot or use absolute path."""
    path_obj = Path(path)

    # If absolute path, use as-is
    if path_obj.is_absolute():
        return str(path_obj)

    # Resolve relative to docroot
    resolved = Path(docroot) / path

    # Add .md extension for files if missing
    if is_file and not resolved.suffix:
        resolved = resolved.with_suffix(".md")

    # Preserve trailing slash for directories
    result = str(resolved)
    if not is_file and path.endswith("/") and not result.endswith("/"):
        result += "/"

    return result


def get_project_name() -> str:
    """Get project name from current directory basename."""
    return Path.cwd().name


def validate_config(config_values: dict[str, str]) -> bool:
    """Validate configuration values for file and directory existence."""
    config = Config()

    for attr_name in dir(config):
        if not attr_name.startswith("_"):
            attr = getattr(config, attr_name)
            if isinstance(attr, ConfigOption) and attr.name in config_values:
                path_value = config_values[attr.name]
                path_obj = Path(path_value)

                # Check if path exists
                if not path_obj.exists():
                    return False

                # Check if it's the right type (file vs directory)
                if attr.is_file and not path_obj.is_file():
                    return False
                elif not attr.is_file and not path_obj.is_dir():
                    return False

    return True


def main() -> click.Command:
    """Main CLI entry point for MCP server."""
    config = Config()

    # Get all config options dynamically
    options = []
    for attr_name in dir(config):
        if not attr_name.startswith("_"):
            attr = getattr(config, attr_name)
            if isinstance(attr, ConfigOption):
                options.append(attr)

    @click.command()
    def cli_main(**kwargs: Any) -> None:
        """MCP server with configurable paths."""
        from .server import create_server_with_config

        # Create mapping from CLI parameter names to ConfigOption names
        param_to_option = {}
        for option in options:
            # Extract parameter name from CLI long option (remove -- and convert to valid Python identifier)
            param_name = option.cli_long.lstrip('--')
            param_to_option[param_name] = option.name

        # Resolve configuration from CLI args, env vars, and defaults
        resolved_config = {}
        for option in options:
            # Check if CLI arg was provided using the parameter mapping
            cli_param_name = option.cli_long.lstrip('--')
            if cli_param_name in kwargs and kwargs[cli_param_name] is not None:
                resolved_config[option.name] = kwargs[cli_param_name]
            else:
                env_value = os.environ.get(option.env_var)
                if env_value is not None:
                    resolved_config[option.name] = env_value
                else:
                    default_val = option.default() if callable(option.default) else option.default
                    resolved_config[option.name] = default_val

        # Create and start server
        create_server_with_config(resolved_config)
        # TODO: Actually start the MCP server
        click.echo(f"Starting MCP server with config: {resolved_config}")

    # Add options dynamically
    for option in options:
        default_val = option.default() if callable(option.default) else option.default
        cli_main = click.option(
            option.cli_short, option.cli_long, envvar=option.env_var, default=default_val, help=option.description
        )(cli_main)

    return cli_main


def cli_main() -> None:
    """Console script entry point."""
    command = main()
    command()
