"""Main CLI entry point for MCP server."""

import os
from typing import Any, Dict, cast
import click
import contextlib
from .config import Config
from .logging_config import get_logger
from .naming import config_filename

logger = get_logger(__name__)


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
                    new_dir = dir_value if dir_value else existing_category["dir"]

                    # Set file patterns
                    if file_value and file_value != "none":
                        if category_name == "lang":
                            new_patterns = [f"{file_value}.md"]
                        else:
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

    logger.debug("Creating server with configuration")
    # Create server with resolved configuration
    create_server_with_config(config)

    if mode == "stdio":
        logger.info("Starting MCP server in stdio mode")
        # Start MCP server in stdio mode
        try:
            mcp.run()
        except (BrokenPipeError, KeyboardInterrupt):
            logger.debug("MCP server shutdown (pipe closed or interrupted)")
        return "MCP server started in stdio mode"
    else:
        logger.warning(f"Unsupported server mode: {mode}")
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

    @click.command()
    @click.argument("mode", required=False, default="stdio")
    def cli_main(mode: str, **kwargs: Any) -> None:
        """MCP server with configurable paths.

        MODE: Server mode - 'stdio' (default)
        """
        # Validate and parse mode
        try:
            mode_type, mode_config = validate_mode(mode)
        except click.BadParameter as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()

        # Resolve configuration from CLI args, env vars, and defaults
        resolved_config = {}

        # Handle config file path first
        config_file_path = None
        global_config = False

        # Check for global config flag
        if "no_global" in kwargs and kwargs["no_global"]:
            # --no-global overrides everything
            global_config = False
        elif "global_config" in kwargs and kwargs["global_config"]:
            global_config = True
            config_file_path = config.get_global_config_path()
        elif os.environ.get("MG_CONFIG_GLOBAL"):
            global_config = True
            config_file_path = config.get_global_config_path()

        # Check for custom config file path (overrides global)
        if "config" in kwargs and kwargs["config"] is not None:
            config_file_path = kwargs["config"]
        elif os.environ.get("MG_CONFIG"):
            config_file_path = os.environ.get("MG_CONFIG")
        elif not global_config:
            # Use default config file
            config_file_path = config_filename()

        # Handle directory vs file logic
        if config_file_path and not global_config:
            # Resolve relative to current directory
            if not os.path.isabs(config_file_path):
                config_file_path = os.path.join(os.getcwd(), config_file_path)

            # If it's a directory, add the config filename (without leading dot)
            if os.path.isdir(config_file_path):
                config_file_path = os.path.join(config_file_path, "mcp-server-guide.config.json")

        # Add config file path to resolved config
        resolved_config["config_filename"] = config_file_path

        for option in options:
            # Skip config-related options as they're handled above
            if option.name in ["config", "global_config", "no_global"]:
                continue

            # Check if CLI arg was provided using the parameter mapping
            cli_param_name = option.cli_long.lstrip("--")
            if cli_param_name in kwargs and kwargs[cli_param_name] is not None:
                resolved_config[option.name] = kwargs[cli_param_name]
            else:
                env_value = os.environ.get(option.env_var)
                if env_value is not None:
                    resolved_config[option.name] = env_value
                else:
                    default_val = option.default() if callable(option.default) else option.default
                    resolved_config[option.name] = default_val

        # Add mode config to resolved config
        resolved_config["mode"] = mode_type
        if mode_config:
            resolved_config["mode_config"] = mode_config

        # Setup logging based on configuration
        from .logging_config import setup_logging

        log_level = resolved_config.get("log_level", "OFF")
        log_file = resolved_config.get("log_file", "")
        log_console = resolved_config.get("log_console", True)

        # For stdio mode, disable console logging by default unless explicitly enabled
        if mode_type == "stdio" and "log_console" not in kwargs:
            log_console = False

        setup_logging(log_level or "INFO", log_file or "", bool(log_console))

        # Configure built-in categories from CLI
        configure_builtin_categories(resolved_config)

        # Log startup information
        logger.info(f"Starting MCP server in {mode_type} mode")
        logger.debug(f"Configuration: {resolved_config}")

        # Start MCP server
        result = start_mcp_server(mode_type, resolved_config)

        # Only echo result if we're not in stdio mode (to avoid breaking protocol)
        if mode_type != "stdio":
            with contextlib.suppress(OSError):
                click.echo(result)

    # Add options dynamically
    for option in options:
        default_val = option.default() if callable(option.default) else option.default

        # Handle boolean options (log_console)
        if option.name == "log_console":
            cli_main = click.option(
                option.cli_long,
                "--no-log-console",
                envvar=option.env_var,
                default=default_val,
                help=option.description,
                is_flag=True,
            )(cli_main)
        else:
            # Regular options - only add cli_short if it's not empty
            if option.cli_short:
                cli_main = click.option(
                    option.cli_short,
                    option.cli_long,
                    envvar=option.env_var,
                    default=default_val,
                    help=option.description,
                )(cli_main)
            else:
                cli_main = click.option(
                    option.cli_long, envvar=option.env_var, default=default_val, help=option.description
                )(cli_main)

    return cast(click.Command, cli_main)


def cli_main() -> None:
    """Console script entry point."""
    command = main()
    command()
