"""Main CLI entry point for MCP server."""

import os
from typing import Any, Dict, cast
import click
import contextlib
from contextvars import ContextVar
from .config import Config
from .logging_config import get_logger
from .path_resolver import LazyPath

logger = get_logger()

# Thread-safe storage for CLI configuration using contextvars
_deferred_builtin_config: ContextVar[Dict[str, Any]] = ContextVar("deferred_builtin_config", default={})


def resolve_config_path(config_path: str | None) -> LazyPath | None:
    """Resolve config file path with client-relative defaults.

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


def setup_early_logging(mode: str, **kwargs: Any) -> None:
    """Setup early logging before configuration resolution.

    Args:
        mode: Server mode (stdio, etc.)
        **kwargs: CLI arguments containing logging options
    """
    from .logging_config import setup_logging

    # Get basic logging config from CLI args for early setup
    early_log_level = kwargs.get("log_level", "INFO")
    early_log_file = kwargs.get("log_file", "")
    early_log_console = kwargs.get("log_console", True)
    early_log_json = kwargs.get("log_json", False)

    # For stdio mode, disable console logging by default unless explicitly enabled
    if mode == "stdio" and "log_console" not in kwargs:
        early_log_console = False

    # Force file logging for debugging if log_file is specified
    if early_log_file:
        early_log_console = True  # Also enable console for debugging

    setup_logging(early_log_level or "INFO", early_log_file or "", bool(early_log_console), bool(early_log_json))


def setup_final_logging(resolved_config: Dict[str, Any], mode_type: str, **kwargs: Any) -> None:
    """Setup final logging with resolved configuration.

    Args:
        resolved_config: Resolved configuration dictionary
        mode_type: Server mode type
        **kwargs: CLI arguments for override detection
    """
    from .logging_config import setup_logging

    # Re-setup logging with final configuration (in case it changed)
    log_level = resolved_config.get("log_level", "OFF")
    log_file = resolved_config.get("log_file", "")
    log_console = resolved_config.get("log_console", True)
    log_json = resolved_config.get("log_json", False)

    # For stdio mode, disable console logging by default unless explicitly enabled
    if mode_type == "stdio" and "log_console" not in kwargs:
        log_console = False

    setup_logging(log_level or "INFO", log_file or "", bool(log_console), bool(log_json))


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
    logger.debug(f"Validating mode: {mode}")

    if mode == "stdio":
        logger.debug("Using stdio mode")
        return ("stdio", "")

    logger.warning(f"Invalid mode specified: {mode}")
    logger.error(f"Program exiting due to invalid mode: {mode}")
    raise click.BadParameter(f"Invalid mode: {mode}. Use 'stdio'")


async def configure_builtin_categories(resolved_config: Dict[str, Any]) -> None:
    """Configure built-in categories from CLI arguments."""
    from .tools.category_tools import update_category, list_categories

    # CLI argument to category mappings
    cli_mappings = [
        ("guidesdir", "guide", "guide"),
        ("langsdir", "lang", "lang"),
        ("contextdir", "context", "context"),
    ]

    for dir_key, file_key, category_name in cli_mappings:
        dir_value = resolved_config.get(dir_key)
        file_value = resolved_config.get(file_key)

        if dir_value or file_value:
            try:
                categories_result = await list_categories()

                # Find existing built-in category
                existing_category = None
                builtin_categories = categories_result.get("categories", {}).get("builtin_categories", [])
                for cat in builtin_categories:
                    if cat["name"] == category_name:
                        existing_category = cat
                        break

                if existing_category:
                    # Update category with CLI values
                    new_dir = dir_value or existing_category["dir"]

                    # Set file patterns
                    if file_value and file_value != "none":
                        new_patterns = [f"{file_value}.md"]
                    else:
                        new_patterns = existing_category["patterns"]

                    # Update the category
                    await update_category(
                        name=category_name,
                        dir=new_dir,
                        patterns=new_patterns,
                        description=existing_category["description"],
                    )

            except Exception:
                logger.warning(f"Failed to configure category {category_name}")


def start_mcp_server(mode: str, config: Dict[str, Any]) -> str:
    """Start MCP server in specified mode."""
    from .server import mcp, create_server_with_config

    logger.debug("Starting MCP server configuration")
    logger.debug(f"Mode: {mode}")
    logger.debug(f"Config keys: {list(config.keys())}")

    try:
        logger.debug("Creating server with configuration")
        # Create server with resolved configuration
        create_server_with_config(config)
        logger.debug("Server configuration completed successfully")
    except Exception as e:
        logger.error(f"FATAL: Server configuration failed during initialization: {e}", exc_info=True)
        # Force flush before re-raising
        for handler in logger.handlers:
            handler.flush()
        raise

    if mode == "stdio":
        logger.info("Starting MCP server in stdio mode")
        # Start MCP server in stdio mode
        try:
            if mcp is None:
                logger.error("MCP server not initialized, cannot start")
                return "Server initialization failed"
            mcp.run()
            logger.info("MCP server shutdown normally (exit code 0)")
        except (BrokenPipeError, KeyboardInterrupt):
            logger.debug("MCP server shutdown (pipe closed or interrupted)")
            logger.info("MCP server shutdown due to interruption (exit code 0)")
        except Exception as e:
            logger.error(f"FATAL: MCP server crashed during runtime: {e}", exc_info=True)
            # Force flush before re-raising
            for handler in logger.handlers:
                handler.flush()
            raise
        return "MCP server started in stdio mode"
    else:
        logger.error(f"Program exiting due to unsupported mode: {mode}")
        raise ValueError(f"Unsupported mode: {mode}")


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
    def cli_main(mode: str, **kwargs: Any) -> None:
        """MCP server with configurable paths.

        MODE: Server mode - 'stdio' (default)
        """
        # Handle version flag first
        if kwargs.get("version"):
            from .naming import MCP_GUIDE_VERSION, mcp_name

            click.echo(f"{mcp_name()} {MCP_GUIDE_VERSION}")
            return

        try:
            # Setup early logging FIRST - before any other operations
            from .logging_config import setup_logging

            # Get basic logging config from CLI args for early setup
            early_log_level = kwargs.get("log_level", "INFO")
            early_log_file = kwargs.get("log_file", "")
            early_log_console = kwargs.get("log_console", True)
            early_log_json = kwargs.get("log_json", False)

            # For stdio mode, disable console logging by default unless explicitly enabled
            if mode == "stdio" and "log_console" not in kwargs:
                early_log_console = False

            # Force file logging for debugging if log_file is specified
            if early_log_file:
                early_log_console = True  # Also enable console for debugging

            setup_logging(
                early_log_level or "INFO", early_log_file or "", bool(early_log_console), bool(early_log_json)
            )

            logger.info("=== MCP Server Initialization Starting ===")
            logger.info(
                f"Early logging setup: level={early_log_level}, file={early_log_file}, console={early_log_console}"
            )
            logger.debug(f"CLI arguments: mode={mode}, kwargs={kwargs}")

            # Force flush after initial messages
            for handler in logger.handlers:
                handler.flush()

            # Validate and parse mode
            try:
                mode_type, mode_config = validate_mode(mode)
                logger.debug(f"Mode validation successful: {mode_type}, {mode_config}")
            except click.BadParameter as e:
                logger.error(f"CLI validation failed: {e}")
                click.echo(f"Error: {e}", err=True)
                raise click.Abort()

            # Resolve configuration from CLI args, env vars, and defaults
            logger.debug("Starting configuration resolution")
            resolved_config = resolve_cli_config(config, **kwargs)

            # Resolve config file path from CLI kwargs (not from resolved_config)
            config_file_path = resolve_config_file_path(kwargs)

            # Add config file path to resolved config
            resolved_config["config_filename"] = config_file_path

            try:
                pass  # Config resolution now handled by resolve_cli_config()
            except Exception as e:
                logger.error(f"FATAL: Configuration option resolution failed: {e}", exc_info=True)
                raise

            # Add mode config to resolved config
            resolved_config["mode"] = mode_type
            if mode_config:
                resolved_config["mode_config"] = mode_config

            # Re-setup logging with final configuration (in case it changed)
            log_level = resolved_config.get("log_level", "OFF")
            log_file = resolved_config.get("log_file", "")
            log_console = resolved_config.get("log_console", True)
            log_json = resolved_config.get("log_json", False)

            # For stdio mode, disable console logging by default unless explicitly enabled
            if mode_type == "stdio" and "log_console" not in kwargs:
                log_console = False

            setup_logging(log_level or "INFO", log_file or "", bool(log_console), bool(log_json))

            # Log startup information
            logger.info(f"MCP server starting up in {mode_type} mode")

            # Log resolved configuration as single JSON block
            import json

            logger.debug(f"Resolved configuration: {json.dumps(resolved_config, indent=2, default=str)}")

            # Store built-in categories config for deferred async processing
            logger.debug("Storing built-in categories config for async processing")
            _deferred_builtin_config.set(resolved_config.copy())

            # Start MCP server
            logger.debug("Starting MCP server")
            try:
                result = start_mcp_server(mode_type, resolved_config)
            except Exception as e:
                logger.error(f"FATAL: Failed to start MCP server: {e}", exc_info=True)
                logger.error("=== MCP SERVER STARTUP FAILED ===")
                logger.error("Check the error details above for the root cause")
                # Force flush all handlers before re-raising
                for handler in logger.handlers:
                    handler.flush()
                raise

            # Only echo result if we're not in stdio mode (to avoid breaking protocol)
            if mode_type != "stdio":
                with contextlib.suppress(OSError):
                    click.echo(result)

        except (KeyboardInterrupt, SystemExit):
            # Re-raise these immediately without logging
            raise
        except Exception as e:
            # Comprehensive error handling with stderr logging
            import sys
            import traceback

            try:
                # Try to log with the configured logger
                logger.error(f"FATAL: CLI execution failed: {e}", exc_info=True)
                logger.error("=== FULL TRACEBACK ===")
                logger.error(traceback.format_exc())

                # Force flush all handlers
                for handler in logger.handlers:
                    handler.flush()
            except Exception:
                # If logging fails, write directly to stderr
                print(f"FATAL ERROR: {e}", file=sys.stderr)
                print("=== FULL TRACEBACK ===", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()

            # Re-raise the exception
            raise

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
            # Regular options with updated metavar for patterns
            metavar = None
            if option.name in ["guide", "lang", "context"]:
                metavar = "PATTERNS"
            elif option.name in ["docroot", "guidesdir", "langsdir", "contextdir"]:
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
    """Console script entry point."""
    try:
        command = main()
        command()
    except Exception as e:
        # Last resort error handling - try to log if possible
        try:
            logger = get_logger()
            logger.error(f"UNHANDLED EXCEPTION in CLI main: {e}", exc_info=True)
            logger.error("=== MCP SERVER CRASHED DURING STARTUP ===")
            # Force flush
            for handler in logger.handlers:
                handler.flush()
        except Exception:
            # If logging fails, print to stderr as last resort
            import sys
            import traceback

            print(f"FATAL ERROR: {e}", file=sys.stderr)
            print("=== FULL TRACEBACK ===", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
        raise
