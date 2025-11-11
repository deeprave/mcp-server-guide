"""Installation script for mcp-server-guide templates and configuration."""

import shutil
import sys
from pathlib import Path
from typing import Optional

import click
import yaml


def get_templates_dir() -> Path:
    """Get the templates directory from the installed package.

    Returns:
        Path to the templates directory

    Raises:
        FileNotFoundError: If templates directory cannot be found
    """
    # First, try to find templates relative to this script's location
    # This works when running from the installed package
    script_dir = Path(__file__).parent
    package_templates = script_dir.parent / "templates"

    if package_templates.exists():
        return package_templates

    # Fallback: look in the package installation directory
    try:
        import mcp_server_guide

        pkg_path = Path(mcp_server_guide.__file__).parent.parent.parent
        fallback_templates = pkg_path / "templates"
        if fallback_templates.exists():
            return fallback_templates
    except ImportError:
        pass

    raise FileNotFoundError(
        "Templates directory not found. This may indicate an incomplete installation. "
        "Please ensure mcp-server-guide is properly installed."
    )


def get_config_dir() -> Path:
    """Get the config directory, creating it if necessary.

    Returns:
        Path to ~/.config/mcp-server-guide
    """
    config_dir = Path.home() / ".config" / "mcp-server-guide"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def prompt_install_location() -> Path:
    """Prompt user for template installation location.

    Returns:
        Path where user wants to install templates
    """
    default_location = Path.home() / ".local" / "share" / "mcp-server-guide" / "templates"

    click.echo("\n" + "=" * 70)
    click.echo("MCP Server Guide - Template Installation")
    click.echo("=" * 70)
    click.echo("\nThis will install template files and create a configuration file.")
    click.echo(f"Default location: {default_location}")
    click.echo("\nYou can specify a custom location or press Enter for the default.")

    user_input = click.prompt("Installation path", default=str(default_location), type=str)
    install_path = Path(user_input).expanduser()

    return install_path


def copy_templates(source: Path, destination: Path) -> None:
    """Copy templates from source to destination.

    Args:
        source: Source templates directory
        destination: Destination path

    Raises:
        FileNotFoundError: If source doesn't exist
        IOError: If copy operation fails
    """
    if not source.exists():
        raise FileNotFoundError(f"Source templates directory not found: {source}")

    # Create destination directory if it doesn't exist
    destination.mkdir(parents=True, exist_ok=True)

    # Copy all templates
    if destination.exists() and any(destination.iterdir()):
        if not click.confirm(f"\n{destination} already contains files. Overwrite?", default=False):
            click.echo("Installation cancelled.")
            sys.exit(0)
        # Remove existing content
        shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)

    # Copy templates
    for item in source.iterdir():
        if item.is_dir():
            shutil.copytree(item, destination / item.name)
        else:
            shutil.copy2(item, destination / item.name)

    click.echo(f"✓ Templates copied to: {destination}")


def create_config(docroot: Path) -> None:
    """Create or update the configuration file.

    Args:
        docroot: Path to the document root (templates directory)
    """
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"

    config_data = {
        "docroot": str(docroot.resolve()),
    }

    try:
        with open(config_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        click.echo(f"✓ Configuration created: {config_file}")
        click.echo(f"  docroot: {config_data['docroot']}")
    except IOError as e:
        click.echo(f"✗ Failed to create configuration file: {e}", err=True)
        raise


def main(install_path: Optional[str] = None) -> None:
    """Main installation routine.

    Args:
        install_path: Optional path to install templates to. If not provided, user will be prompted.
    """
    try:
        # Get templates from package
        templates_source = get_templates_dir()
        click.echo(f"\n✓ Found templates at: {templates_source}")

        # Determine installation path
        if install_path:
            install_destination = Path(install_path).expanduser()
        else:
            install_destination = prompt_install_location()

        # Confirm before proceeding
        click.echo("\nInstallation details:")
        click.echo(f"  Source: {templates_source}")
        click.echo(f"  Destination: {install_destination}")

        if not click.confirm("\nProceed with installation?", default=True):
            click.echo("Installation cancelled.")
            sys.exit(0)

        # Copy templates
        copy_templates(templates_source, install_destination)

        # Create configuration
        create_config(install_destination)

        click.echo("\n" + "=" * 70)
        click.echo("✓ Installation completed successfully!")
        click.echo("=" * 70)
        click.echo("\nNext steps:")
        click.echo("1. The templates are installed at the location specified above")
        click.echo("2. Configuration saved to: ~/.config/mcp-server-guide/config.yaml")
        click.echo("3. Start the server with: mcp-server-guide")
        click.echo()

    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Unexpected error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    "--path",
    "-p",
    default=None,
    type=click.Path(),
    help="Installation path for templates (uses default if not specified)",
)
def cli_main(path: Optional[str]) -> None:
    """Install MCP Server Guide templates and configuration.

    This tool copies the template files to your desired location and creates
    a configuration file at ~/.config/mcp-server-guide/config.yaml.
    """
    main(install_path=path)


if __name__ == "__main__":
    cli_main()
