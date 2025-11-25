#!/usr/bin/env python3
"""Installation script for mcp-server-guide templates and configuration."""

import asyncio
import contextlib
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Tuple

import aiofiles
import click
import yaml

from mcp_server_guide.config_paths import get_default_config_file, get_default_docroot
from mcp_server_guide.exceptions import SecurityError
from mcp_server_guide.security.path_validator import PathValidator
from mcp_server_guide.utils.installation_utils import get_templates_dir


def prompt_install_location(default_location: Path, yes: bool = False) -> Path:
    """Prompt user for template installation location.

    Returns:
        Path where the user wants to install templates
    """
    if yes:
        user_input = default_location
    else:
        click.echo("\n" + "=" * 70)
        click.echo("MCP Server Guide - Template Installation")
        click.echo("=" * 70)
        click.echo("\nThis will install template files and create/update a configuration file.")
        click.echo(f"Default location: {default_location}")
        click.echo("\nYou can specify a custom location or press Enter for the default.")
        user_input = click.prompt("Installation path", default=str(default_location), type=str)

    resolved_path = Path(user_input).expanduser()

    # Only validate user-provided paths (not default paths)
    if not yes and str(user_input) != str(default_location):
        # Create a validator with reasonable allowed roots
        allowed_roots: list[str | Path] = [str(Path.home()), "/tmp", "/var/tmp"]
        validator = PathValidator(allowed_roots)
        try:
            validator.validate_path(str(resolved_path), Path.home())
        except SecurityError as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort() from e

    return resolved_path


async def compare_files(file1: Path, file2: Path) -> bool:
    """Compare two files by computing their SHA256 hashes.

    Args:
        file1: First file path
        file2: Second file path

    Returns:
        True if files are identical, False otherwise
    """

    async def file_hash(filepath: Path) -> str:
        """Compute the SHA256 hash of a file asynchronously."""
        hasher = hashlib.sha256()
        async with aiofiles.open(filepath, "rb") as f:
            while chunk := await f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    try:
        # Quick size check first
        if file1.stat().st_size != file2.stat().st_size:
            return False

        # Compute and compare hashes
        hash1 = await file_hash(file1)
        hash2 = await file_hash(file2)

        return hash1 == hash2
    except (OSError, IOError):
        return False


async def _copy_item(
    src_item: Path,
    dst_item: Path,
    verbose: int = 0,
    src_root: Optional[Path] = None,
    dst_root: Optional[Path] = None,
) -> int:
    """Copy a single file or directory, backing up existing files if different.

    Args:
        src_item: Source path (file or directory)
        dst_item: Destination path
        verbose: Verbosity level (0=minimal, 1=verbose, 2=extra verbose)
        src_root: Root source path for relative path display
        dst_root: Root destination path for relative path display

    Returns:
        Count of files copied or updated (excludes skipped files)
    """

    async def backup_existing(dest_item: Path, src_path: Path) -> None:
        # Destination is a file, not a directory - back it up
        backup_path = dest_item.parent / f"orig.{dest_item.name}"
        dest_item.rename(backup_path)
        if verbose > 0:
            _src = src_path.relative_to(src_root) if src_root else src_path
            _dst = dest_item.relative_to(dst_root) if dst_root else dest_item
            click.echo(f"  {_src} -> {_dst} Updated (with backup)")

    if src_item.is_dir():
        count = 0
        if dst_item.exists():
            if dst_item.is_dir():
                # For directories, recursively copy contents
                for child in src_item.iterdir():
                    count += await _copy_item(child, dst_item / child.name, verbose, src_root, dst_root)
                return count
            else:
                await backup_existing(dst_item, src_item)
        # Create and populate the directory
        dst_item.mkdir(parents=True, exist_ok=True)
        for child in src_item.iterdir():
            count += await _copy_item(child, dst_item / child.name, verbose, src_root, dst_root)
        return count
    else:
        # It's a file
        if dst_item.exists():
            if dst_item.is_dir():
                # Destination is a directory, remove it first
                shutil.rmtree(dst_item)
            elif await compare_files(src_item, dst_item):
                # Files are identical, skip
                if verbose > 1:
                    src = src_item.relative_to(src_root) if src_root else src_item
                    dst = dst_item.relative_to(dst_root) if dst_root else dst_item
                    click.echo(f"  {src} -> {dst} Skipped (identical)")
                return 0
            else:
                await backup_existing(dst_item, src_item)
        else:
            # New file
            if verbose > 0:
                src = src_item.relative_to(src_root) if src_root else src_item
                dst = dst_item.relative_to(dst_root) if dst_root else dst_item
                click.echo(f"  {src} -> {dst} Copied (new)")
        # Copy the file
        dst_item.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_item, dst_item)
        return 1


async def copy_templates_with_interaction(source: Path, destination: Path, verbose: int = 0) -> int:
    """Copy templates from source to destination with user interaction.

    When copying:
    - If source and destination files are identical, they're skipped
    - If files differ, the existing destination file is backed up to orig.<filename>

    Args:
        source: Source templates directory
        destination: Destination path
        verbose: Verbosity level (0=minimal, 1=verbose, 2=extra verbose)

    Returns:
        Count of files copied or updated (excludes skipped files)

    Raises:
        FileNotFoundError: If the source file doesn't exist.
        IOError: If the copy operation fails
    """
    if not source.exists():
        raise FileNotFoundError(f"Source templates directory not found: {source}")

    # Create the destination directory if it doesn't exist
    destination.mkdir(parents=True, exist_ok=True)

    # Copy templates
    click.echo("\nCopying templates:")
    count = 0
    for item in source.iterdir():
        if item.name.startswith("."):
            continue
        count += await _copy_item(item, destination / item.name, verbose, source, destination)

    if count > 0:
        click.echo(f"✓ Templates copied to: {destination} ({count} file{'s' if count != 1 else ''} updated)")
    else:
        click.echo(f"✓ Templates up to date: {destination}")

    return count


async def create_or_update_config(
    docroot: Path, config_path: Optional[str] = None, install_path: Optional[str] = None
) -> Tuple[Path, Path]:
    """Create or update the configuration file.
        if install_path is None, use the existing docroot (user not overriding)
        Otherwise set it to the provided docroot

    Args:
        docroot: Path to the document root (templates directory)
        install_path: Optional install_path provided by user
        config_path: Optional path to config file.
        If not provided, use the default location.
    """
    config_file = Path(config_path).expanduser() if config_path else get_default_config_file()
    # Create the parent directory if it doesn't exist
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Try to read and parse the existing config file
    config_data = {}
    if config_file.exists():
        with contextlib.suppress(IOError, yaml.YAMLError):
            with open(config_file, "r") as f:
                existing_config = yaml.safe_load(f)
                if existing_config and isinstance(existing_config, dict):
                    config_data = existing_config
                    # adopt the existing docroot if not overriding
                    if install_path is None and "docroot" in config_data:
                        docroot = Path(config_data["docroot"]).expanduser()
    # Add or update the docroot element
    config_data["docroot"] = str(docroot.resolve())

    with open(config_file, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
    click.echo(f"✓ Configuration: {config_file}")
    click.echo(f"  with docroot: {config_data['docroot']}")
    return docroot, config_file


async def main(
    install_path: Optional[str] = None, config_path: Optional[str] = None, verbose: int = 0, yes: bool = False
) -> None:
    """Main installation routine.

    Args:
        install_path: Optional path to install templates to.
        If not provided, the user will be prompted.
        config_path: Optional path to config file.
        verbose: Verbosity level (0=minimal, 1=verbose, 2=extra verbose)
        yes: Whether to ask for user confirmation.
    """
    try:
        # Get templates from the package using the shared module
        templates_source = get_templates_dir()
        if verbose > 0:
            click.echo(f"\n✓ Found templates at: {templates_source}")

        # Determine the installation path
        if install_path:
            install_destination = Path(install_path).expanduser()
        else:
            install_destination = get_default_docroot()

        # Create configuration
        install_destination, config_file = await create_or_update_config(
            install_destination, config_path=config_path, install_path=install_path
        )

        install_destination = prompt_install_location(install_destination, yes)

        # Confirm before proceeding - only show details if verbose
        if verbose > 0:
            click.echo("\nInstallation details:")
            click.echo(f"  Source: {templates_source}")
            click.echo(f"  Destination: {install_destination}")

        if not yes and not click.confirm("\nProceed with installation?", default=True):
            click.echo("Installation cancelled.")
            raise click.Abort()

        # Copy templates with user interaction
        await copy_templates_with_interaction(templates_source, install_destination, verbose=verbose)

        if verbose > 0:
            click.echo("\n" + "=" * 70)
            click.echo("✓ Installation completed successfully!")
            click.echo("=" * 70)
            click.echo("\nNext steps:")
            click.echo(f"1. The templates are installed or updated: {install_destination}")
            click.echo(f"2. Configuration saved to: {config_file}")
            click.echo()

    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        click.Abort(2)
    except Exception as e:
        click.echo(f"✗ Unexpected error: {e}", err=True)
        click.Abort(1)


@click.command()
@click.option(
    "--path",
    "-p",
    default=None,
    type=click.Path(),
    help="Installation path for templates (uses default if not specified)",
)
@click.option(
    "--config",
    "-c",
    default=None,
    type=click.Path(),
    help="Path to configuration file",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    default=0,
    help="Increase verbosity (-v for verbose, -vv for extra verbose)",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Proceed without confirmation",
)
def cli_main(path: Optional[str], config: Optional[str], verbose: int, yes: bool) -> None:
    """Install MCP Server Guide templates and configuration.

    This tool copies the template files to your desired location and creates
    a configuration file at ~/.config/mcp-server-guide/config.yaml.
    """
    asyncio.run(main(install_path=path, config_path=config, verbose=verbose, yes=yes))


if __name__ == "__main__":
    cli_main()
