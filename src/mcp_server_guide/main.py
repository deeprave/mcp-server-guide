"""Main CLI entry point for MCP server."""

import logging
import os
import sys
import asyncio
from typing import Any, Dict, cast
import click
from contextvars import ContextVar
from .config import Config
from .logging_config import get_logger
from .path_resolver import LazyPath

# Logger will be initialized after logging setup
logger = None


def _get_safe_logger() -> logging.Logger:
    """Get logger safely, handling case where global logger is not yet initialized."""
    global logger
    return get_logger() if logger is None else logger


# Thread-safe storage for CLI configuration using contextvars
_deferred_builtin_config: ContextVar[Dict[str, Any]] = ContextVar("deferred_builtin_config", default={})


def resolve_config_path(config_path: str | None) -> LazyPath | None:
    """Resolve server config file path with environment variable and user path expansion.

    Args:
        config_path: Config file path

    Returns:
        Resolved Path object
    """
    # Handle environment variable expansion first (supports $VAR and ${VAR})
    if config_path:
        if "$" in config_path:
            expanded = os.path.expandvars(config_path)
            if expanded != config_path:  # Variable was expanded
                config_path = expanded

        if config_path.startswith("~"):
            config_path = os.path.expanduser(config_path)

        return LazyPath(config_path)
    return None


def resolve_cli_config(config_obj: Config, **kwargs: Any) -> Dict[str, Any]:
    """Resolve configuration from CLI args, environment variables, and defaults.

    Args:
        config_obj: Config object with all available options
        **kwargs: CLI arguments passed from Click

    Returns:
        Dictionary with resolved configuration values
    """
    resolved_config = {}

    # Get all config options dynamically
    options = []
    for attr_name in dir(config_obj):
        if not attr_name.startswith("_"):
            attr = getattr(config_obj, attr_name)
            if hasattr(attr, "cli_long"):  # Check if it's a ConfigOption
                options.append(attr)

    for option in options:
        # Click converts hyphens to underscores in parameter names
        cli_param_name = option.cli_long.lstrip("--").replace("-", "_")

        if cli_param_name in kwargs and kwargs[cli_param_name] is not None:
            resolved_config[option.name] = kwargs[cli_param_name]
        else:
            env_value = os.environ.get(option.env_var)
            if env_value is not None:
                resolved_config[option.name] = env_value
            else:
                default_val = option.default() if callable(option.default) else option.default
                resolved_config[option.name] = default_val

    return resolved_config


def resolve_config_file_path(kwargs: Dict[str, Any]) -> LazyPath | None:
    """Resolve config file path from CLI args, environment variables, and defaults.

    Args:
        kwargs: CLI arguments dictionary
        config_obj: Config object (unused, kept for compatibility)

    Returns:
        Resolved config file path or None
    """
    config_file_path = None

    # Precedence order (highest to lowest):
    # 1. --config FILENAME (always wins)
    # 2. MG_CONFIG environment variable
    # 3. Default config file

    if "config" in kwargs and kwargs["config"] is not None:
        # Highest priority: explicit --config argument
        config_file_path = kwargs["config"]
    elif os.environ.get("MG_CONFIG"):
        # Second priority: MG_CONFIG environment variable
        config_file_path = os.environ.get("MG_CONFIG")

    return resolve_config_path(config_file_path)


class CustomHelpFormatter(click.HelpFormatter):
    """Custom help formatter with no wrapping and footnotes."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Override width to prevent wrapping
        kwargs["width"] = 999
        super().__init__(*args, **kwargs)

    def write_dl(self, rows: Any, col_max: Any = None, col_spacing: int = 2) -> None:
        """Override definition list formatting to increase option column width."""
        if col_max is None:
            col_max = 40  # Increase from default ~30 to 40
        super().write_dl(rows, col_max, col_spacing)


class CustomCommand(click.Command):
    """Custom command class to add footnotes to help."""

    def get_help(self, ctx: Any) -> str:
        """Get help text with footnotes."""
        help_text = super().get_help(ctx)

        # Add footnotes
        footnotes = [
            "",
            "Footnotes:",
            "  * comma-separated glob patterns (e.g., *.md,**/*.py)",
            "  ** path relative to docroot",
        ]

        return help_text + "\n".join(footnotes)


# Override click's default formatter
click.Context.formatter_class = CustomHelpFormatter


def validate_mode(mode: str) -> tuple[str, str]:
    """Validate and parse mode argument.

    Returns:
        tuple: (mode_type, mode_config)
        - stdio: ("stdio", "")
    """
    safe_logger = _get_safe_logger()
    safe_logger.debug(f"Validating mode: {mode}")

    if mode == "stdio":
        safe_logger.debug("Using stdio mode")
        return ("stdio", "")

    safe_logger.warning(f"Invalid mode specified: {mode}")
    safe_logger.error(f"Program exiting due to invalid mode: {mode}")
    raise click.BadParameter(f"Invalid mode: {mode}. Use 'stdio'")


async def start_mcp_server(mode: str, config: Dict[str, Any]) -> str:
    """Start MCP server in specified mode."""
    from .server import get_current_server, set_current_config

    safe_logger = _get_safe_logger()
    safe_logger.debug("Starting MCP server configuration in {mode} mode")
    safe_logger.debug(f"Config keys: {list(config.keys())}")

    # Set config for lazy server creation
    set_current_config(config)

    if mode == "stdio":
        safe_logger.info("Starting MCP server in stdio mode")
        # Start MCP server in stdio mode
        try:
            server = await get_current_server()
            if server is not None:
                await server.run_stdio_async()
                safe_logger.info("MCP server shutdown normally (exit code 0)")
            else:
                safe_logger.error("Failed to create server instance")
                return "Failed to create server instance"
        except (BrokenPipeError, KeyboardInterrupt):
            safe_logger.debug("MCP server shutdown (pipe closed or interrupted)")
            safe_logger.info("MCP server shutdown due to interruption (exit code 0)")
        except Exception as e:
            safe_logger.error(f"FATAL: MCP server crashed during runtime: {e}", exc_info=True)
            # Force flush before re-raising
            for handler in safe_logger.handlers:
                handler.flush()
            raise
        return "MCP server started in stdio mode"
    else:
        safe_logger.error(f"Program exiting due to unsupported mode: {mode}")
        raise ValueError(f"Unsupported mode: {mode}")


def parse_cli_arguments() -> Dict[str, Any]:
    """Parse CLI arguments and return configuration dictionary.

    This function only handles CLI parsing and returns the parsed configuration.
    It does NOT start the server - that's handled separately.
    """
    import sys
    from click.testing import CliRunner

    # Get the Click command
    command = main()

    # Use CliRunner to parse arguments
    runner = CliRunner()

    # Parse sys.argv (skip script name)
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    # Invoke the command to get config
    result = runner.invoke(command, args, catch_exceptions=False, standalone_mode=False)

    # The command should return the config dict
    return result.return_value or {}


async def start_server_with_config(config_dict: Dict[str, Any]) -> None:
    """Start server in clean async context with parsed configuration."""
    # Extract mode from config
    mode = config_dict.get("mode", "stdio")

    # Setup logging with CLI arguments
    from .logging_config import setup_consolidated_logging

    setup_consolidated_logging(mode, config_source=config_dict, cli_overrides=config_dict)

    # Initialize logger after logging setup
    global logger
    logger = get_logger()

    logger.info("=== MCP Server Initialization Starting ===")
    logger.debug(f"Starting server with config: {config_dict}")

    # Store built-in categories config for deferred async processing
    logger.debug("Storing built-in categories config for async processing")
    _deferred_builtin_config.set(config_dict.copy())

    # Start MCP server (async call)
    logger.debug("Starting MCP server")
    try:
        result = await start_mcp_server(mode, config_dict)
        logger.info(f"MCP server started successfully: {result}")
    except Exception as e:
        logger.error(f"FATAL: Failed to start MCP server: {e}", exc_info=True)
        logger.error("=== MCP SERVER STARTUP FAILED ===")
        raise


def main() -> click.Command:
    """Main CLI entry point for MCP server."""
    config = Config()

    # Get all config options dynamically
    options = []
    for attr_name in dir(config):
        if not attr_name.startswith("_"):
            attr = getattr(config, attr_name)
            if hasattr(attr, "cli_long"):  # Check if it's a ConfigOption
                options.append(attr)

    @click.command(cls=CustomCommand)
    @click.argument("mode", required=False, default="stdio")
    def cli_main(mode: str, **kwargs: Any) -> Dict[str, Any]:
        """MCP server with configurable paths - CONFIGURATION ONLY.

        MODE: Server mode - 'stdio' (default)

        Returns: Configuration dictionary
        """
        # Handle version flag first
        if kwargs.get("version"):
            from .naming import MCP_GUIDE_VERSION, mcp_name

            click.echo(f"{mcp_name()} {MCP_GUIDE_VERSION}")
            return {}

        # Validate and parse mode
        try:
            mode_type, mode_config = validate_mode(mode)
        except click.BadParameter as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()

        # Resolve configuration from CLI args, env vars, and defaults
        resolved_config = resolve_cli_config(config, **kwargs)

        # Resolve config file path from CLI kwargs
        config_file_path = resolve_config_file_path(kwargs)

        # Add config file path to resolved config
        resolved_config["config_filename"] = config_file_path

        # Add mode config to resolved config
        resolved_config["mode"] = mode_type
        if mode_config:
            resolved_config["mode_config"] = mode_config

        return resolved_config

    # Group options by category for better organization using the 'group' attribute
    from collections import defaultdict

    grouped_options = defaultdict(list)
    for opt in options:
        grouped_options[getattr(opt, "group", "other")].append(opt)

    config_options = grouped_options.get("config", [])
    logging_options = grouped_options.get("logging", [])
    docroot_options = grouped_options.get("docroot", [])
    content_options = grouped_options.get("content", [])
    other_options = grouped_options.get("other", [])

    # Add options in reverse order due to decorator stacking
    # Desired display order: config, logging, docroot, content, other (version/help)
    # Apply in reverse: other, content, docroot, logging, config
    all_grouped_options = config_options + logging_options + docroot_options + content_options + other_options

    for option in all_grouped_options:
        default_val = option.default() if callable(option.default) else option.default

        # Override default for config option to None so it doesn't interfere with --global-config
        if option.name == "config":
            default_val = None

        # Handle boolean flags
        if option.name == "global_config":
            cli_main = click.option(
                "--global-config/--no-global-config",
                is_flag=True,
                envvar=option.env_var,
                default=False,
                help=option.description,
            )(cli_main)
        elif option.name == "log_console":
            cli_main = click.option(
                option.cli_long,
                "--no-log-console",
                envvar=option.env_var,
                default=default_val,
                help=option.description,
                is_flag=True,
            )(cli_main)
        elif option.name == "log_json":
            cli_main = click.option(
                option.cli_long,
                envvar=option.env_var,
                default=False,
                help=option.description,
                is_flag=True,
            )(cli_main)
        elif option.name == "version":
            cli_main = click.option(
                option.cli_long,
                is_flag=True,
                help=option.description,
            )(cli_main)
        else:
            # Regular options with updated metavar
            metavar = None
            if option.name in ["docroot"]:
                metavar = "DIRECTORY"
            elif option.name in ["config", "log_file"]:
                metavar = "FILENAME"
            elif option.name == "log_level":
                metavar = "LEVEL"

            if option.cli_short:
                cli_main = click.option(
                    option.cli_short,
                    option.cli_long,
                    envvar=option.env_var,
                    default=default_val,
                    help=option.description,
                    metavar=metavar,
                )(cli_main)
            else:
                cli_main = click.option(
                    option.cli_long,
                    envvar=option.env_var,
                    default=default_val,
                    help=option.description,
                    metavar=metavar,
                )(cli_main)

    return cast(click.Command, cli_main)


def cli_main() -> None:
    """New clean CLI entry point - parse CLI then start server."""
    try:
        # Phase 1: Parse CLI arguments (sync, returns config)
        config_dict = parse_cli_arguments()

        # Phase 2: Start server with parsed config (async, clean context)
        asyncio.run(start_server_with_config(config_dict))

    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
