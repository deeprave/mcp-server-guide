"""Main CLI entry point for MCP server."""

import os
from typing import Any, Dict, cast
from pathlib import Path
import click
import contextlib
from .config import Config
from .logging_config import get_logger
from .naming import config_filename
from .client_path import ClientPath
from .path_resolver import LazyPath

logger = get_logger()


def resolve_config_path_with_client_defaults(config_path: str) -> Path:
    """Resolve config file path with client-relative defaults.

    Args:
        config_path: Config file path (may be relative, absolute, or URI-prefixed)

    Returns:
        Resolved Path object
    """
    # Handle environment variable expansion first (supports $VAR and ${VAR})
    if "$" in config_path:
        expanded = os.path.expandvars(config_path)
        if expanded != config_path:  # Variable was expanded
            config_path = expanded

    # Handle home directory paths (~, ~username) - bypass client-relative behavior
    if config_path.startswith("~"):
        return Path(config_path).expanduser().resolve()

    # Handle absolute paths - bypass client-relative behavior
    if os.path.isabs(config_path):
        return Path(config_path).resolve()

    # Handle URI-style prefixes using LazyPath
    if any(
        config_path.startswith(prefix)
        for prefix in ["client://", "local://", "server://", "http://", "https://", "file://"]
    ):
        lazy_path = LazyPath(config_path)
        return lazy_path.resolve_sync()

    # Check for unknown URI schemes and raise error (but allow empty schemes to fall through)
    if "://" in config_path:
        scheme = config_path.split("://", 1)[0]
        if scheme:  # Only raise for non-empty schemes
            raise ValueError(f"Unsupported URL scheme: {scheme}://")

    # Default: treat as client-relative path
    client_root = ClientPath.get_primary_root()
    if client_root is not None:
        return client_root / config_path

    # Fallback: server-side resolution
    return Path(config_path).expanduser().resolve()


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
        # Skip config-related options as they're handled separately
        if option.name in ["config", "global_config"]:
            continue

        # Check if CLI arg was provided using the parameter mapping
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


def resolve_config_file_path(kwargs: Dict[str, Any], config_obj: Config) -> str | None:
    """Resolve config file path from CLI args, environment variables, and defaults.

    Args:
        kwargs: CLI arguments dictionary
        config_obj: Config object for accessing global config path

    Returns:
        Resolved config file path or None
    """
    config_file_path = None
    global_config = False

    # Check for global config flag first
    if "global_config" in kwargs and kwargs["global_config"] is not None:
        global_config = kwargs["global_config"]
    elif os.environ.get("MG_CONFIG_GLOBAL"):
        global_config = True

    # Check for custom config file path (overrides global)
    if "config" in kwargs and kwargs["config"] is not None:
        config_file_path = kwargs["config"]
        global_config = False  # Custom config overrides global
    elif os.environ.get("MG_CONFIG"):
        config_file_path = os.environ.get("MG_CONFIG")
        global_config = False  # Env config overrides global
    elif global_config:
        # Use global config path
        config_file_path = config_obj.get_global_config_path()
    else:
        # Use default config file
        config_file_path = config_filename()

    # Handle directory vs file logic and apply client-relative resolution
    if config_file_path and not global_config:
        # Use new client-relative resolution for non-global configs
        resolved_path = resolve_config_path_with_client_defaults(config_file_path)

        # If it's a directory, add the config filename (without leading dot)
        if resolved_path.is_dir():
            config_file_path = str(resolved_path / config_filename().lstrip("."))
        else:
            config_file_path = str(resolved_path)
    elif config_file_path and global_config:
        # Global configs use absolute path resolution
        config_file_path = str(Path(config_file_path).expanduser().resolve())

    return config_file_path


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


def configure_builtin_categories(resolved_config: Dict[str, Any]) -> None:
    """Configure built-in categories from CLI arguments."""
    from .tools.category_tools import update_category

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
                from .tools.category_tools import list_categories

                categories_result = list_categories()

                # Find existing built-in category
                existing_category = None
                for cat in categories_result.get("builtin_categories", []):
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
                    import asyncio

                    asyncio.run(
                        update_category(
                            name=category_name,
                            dir=new_dir,
                            patterns=new_patterns,
                            description=existing_category["description"],
                        )
                    )

            except Exception as e:
                logger.warning(f"Failed to apply CLI arg to category {category_name}: {e}")


def start_mcp_server(mode: str, config: Dict[str, Any]) -> str:
    """Start MCP server in specified mode."""
    from .server import mcp, create_server_with_config

    logger.debug("=== Starting MCP server initialization ===")
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
            logger.debug("About to call mcp.run() - this is where crashes often occur")
            mcp.run()
            logger.info("MCP server shutdown normally (exit code 0)")
        except (BrokenPipeError, KeyboardInterrupt):
            logger.debug("MCP server shutdown (pipe closed or interrupted)")
            logger.info("MCP server shutdown due to interruption (exit code 0)")
        except Exception as e:
            logger.error(f"FATAL: MCP server crashed during runtime: {e}", exc_info=True)
            logger.error("This indicates a runtime failure after successful initialization")
            # Force flush before re-raising
            for handler in logger.handlers:
                handler.flush()
            raise
        return "MCP server started in stdio mode"
    else:
        logger.warning(f"Unsupported server mode: {mode}")
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
            import importlib.metadata

            try:
                version = importlib.metadata.version("mcp-server-guide")
                click.echo(f"mcp-server-guide {version}")
            except importlib.metadata.PackageNotFoundError:
                click.echo("mcp-server-guide version unknown")
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

            # Handle config file path separately (not part of standard config resolution)
            config_file_path = resolve_config_file_path(kwargs, config)

            # Add config file path to resolved config
            resolved_config["config_filename"] = config_file_path
            logger.debug(f"Config file path resolved: {config_file_path}")

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
            logger.info(f"Configuration loaded from: {resolved_config.get('config_filename', 'defaults')}")

            # Log resolved configuration as single JSON block
            import json

            logger.debug(f"Resolved configuration: {json.dumps(resolved_config, indent=2, default=str)}")

            # Configure built-in categories from CLI
            logger.debug("Configuring built-in categories from CLI")
            try:
                configure_builtin_categories(resolved_config)
                logger.debug("Built-in categories configured successfully")
            except Exception as e:
                logger.warning(f"Failed to configure built-in categories: {e}", exc_info=True)

            # Start MCP server
            logger.debug("Starting MCP server")
            try:
                result = start_mcp_server(mode_type, resolved_config)
                logger.info("MCP server started successfully")
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

        # Handle boolean flags
        if option.name == "global_config":
            cli_main = click.option(
                "--global-config/--no-global-config",
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
