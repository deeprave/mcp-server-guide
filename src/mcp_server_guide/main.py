"""Main CLI entry point for MCP server."""

import os
import re
from typing import Any, Dict
import click
from .config import Config
from .logging_config import get_logger

logger = get_logger(__name__)


def validate_mode(mode: str) -> tuple[str, str]:
    """Validate and parse mode argument.

    Returns:
        tuple: (mode_type, mode_config)
        - stdio: ("stdio", "")
        - sse=url: ("sse", "http://localhost:8080/sse")
    """
    logger.debug(f"Validating mode: {mode}")

    if mode == "stdio":
        logger.debug("Using stdio mode")
        return ("stdio", "")

    if mode.startswith("sse="):
        sse_url = mode[4:]  # Remove "sse=" prefix
        logger.debug(f"Parsing SSE URL: {sse_url}")
        # Basic URL validation
        if not re.match(r"^https?://.+", sse_url):
            logger.warning(f"Invalid SSE URL format: {sse_url}")
            raise click.BadParameter(f"Invalid SSE URL format: {sse_url}")
        logger.debug(f"Using SSE mode with URL: {sse_url}")
        return ("sse", sse_url)

    logger.warning(f"Invalid mode specified: {mode}")
    raise click.BadParameter(f"Invalid mode: {mode}. Use 'stdio' or 'sse=http://host/path'")


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
            # Graceful shutdown on pipe close or Ctrl+C
            pass
        return "MCP server started in stdio mode"
    elif mode == "sse":
        # Start MCP server in SSE mode
        sse_url = config.get("mode_config", "http://localhost:8080/sse")
        logger.info(f"Starting MCP server in SSE mode at {sse_url}")

        # Parse URL for host and port
        import urllib.parse

        parsed = urllib.parse.urlparse(sse_url)
        host = parsed.hostname or "localhost"

        # Determine port: explicit port > default for protocol > 8080 fallback
        if parsed.port:
            port = parsed.port
        elif parsed.scheme == "https":
            port = 443
        elif parsed.scheme == "http":
            port = 80
        else:
            port = 8080  # Fallback for development

        logger.debug(f"Binding to {host}:{port}")

        try:
            # Use uvicorn to run the FastMCP server
            import uvicorn
            from typing import cast, Any

            # FastMCP is an ASGI app but not properly typed, so cast it
            uvicorn.run(cast(Any, mcp), host=host, port=port)
        except KeyboardInterrupt:
            logger.debug("SSE server shutdown (interrupted)")
            # Graceful shutdown on Ctrl+C
            pass
        return f"MCP server started in sse mode at {sse_url}"
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

        MODE: Server mode - 'stdio' (default) or 'sse=http://host/path'
        """
        # Validate and parse mode
        try:
            mode_type, mode_config = validate_mode(mode)
        except click.BadParameter as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()

        # Resolve configuration from CLI args, env vars, and defaults
        resolved_config = {}
        for option in options:
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

        setup_logging(log_level, log_file, log_console)

        # Log startup information
        logger.info(f"Starting MCP server in {mode_type} mode")
        logger.debug(f"Configuration: {resolved_config}")

        # Start MCP server
        result = start_mcp_server(mode_type, resolved_config)

        # Only echo result if we're not in stdio mode (to avoid breaking protocol)
        if mode_type != "stdio":
            try:
                click.echo(result)
            except (BrokenPipeError, OSError):
                # Graceful handling if output pipe is closed
                pass

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

    return cli_main


def cli_main() -> None:
    """Console script entry point."""
    command = main()
    command()
