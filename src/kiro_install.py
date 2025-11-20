#!/usr/bin/env python3
"""Kiro installation script for setting up ~/.kiro directory structure."""

import asyncio
import hashlib
import shutil
import sys
import stat
import click
import aiofiles
import aioshutil
from anyio import Path as AsyncPath


def check_kiro_cli_installed() -> bool:
    """Check if kiro-cli is available in PATH.

    Returns:
        bool: True if kiro-cli is found in PATH, False otherwise.
    """
    return shutil.which("kiro-cli") is not None


async def create_directories(base_path: AsyncPath, verbose: bool = False) -> None:
    """Create required directory structure for Kiro installation.

    Creates ~/.kiro and subdirectories: agents, scripts, scripts/consent, scripts/review.

    Args:
        base_path: Base path for Kiro installation (typically ~/.kiro).
        verbose: If True, print detailed progress messages.
    """
    dirs = [
        base_path,
        base_path / "agents",
        base_path / "scripts",
        base_path / "scripts" / "consent",
        base_path / "scripts" / "review",
    ]
    for dir_path in dirs:
        if verbose and not await dir_path.exists():
            click.echo(f"  Creating directory: {dir_path}")
        await dir_path.mkdir(parents=True, exist_ok=True)


async def files_are_identical(src: AsyncPath, dst: AsyncPath) -> bool:
    """Compare two files by computing their SHA256 hashes.

    Uses chunked reading to avoid loading entire files into memory.

    Args:
        src: Source file path.
        dst: Destination file path.

    Returns:
        bool: True if files have identical content, False otherwise.
    """

    async def file_hash(filepath: AsyncPath) -> str:
        """Compute SHA256 hash of a file asynchronously."""
        hasher = hashlib.sha256()
        async with aiofiles.open(filepath, "rb") as f:
            while chunk := await f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    try:
        if not await dst.exists():
            return False

        # Quick size check first
        src_stat = await src.stat()
        dst_stat = await dst.stat()
        if src_stat.st_size != dst_stat.st_size:
            return False

        # Compute and compare hashes
        hash1 = await file_hash(src)
        hash2 = await file_hash(dst)

        return hash1 == hash2
    except (OSError, IOError):
        return False


async def prompt_user_confirmation(file_path: AsyncPath) -> bool:
    """Prompt user for file overwrite confirmation.

    Args:
        file_path: Path to file that would be overwritten.

    Returns:
        bool: True if user confirms overwrite, False otherwise.
    """
    response = input(f"File {file_path} exists and differs. Overwrite? [y/N]: ")
    return response.lower() in ("y", "yes")


async def copy_file_if_needed(
    src: AsyncPath, dst: AsyncPath, auto_yes: bool, verbose: bool = False, rel_path: str = ""
) -> None:
    """Copy file if needed, handling identical/different cases.

    Skips copying if files are identical. Prompts for confirmation if destination
    exists and differs (unless auto_yes is True). Uses aioshutil.copy2 to preserve
    file metadata.

    Args:
        src: Source file path.
        dst: Destination file path.
        auto_yes: If True, skip confirmation prompts.
        verbose: If True, print detailed progress messages.
        rel_path: Relative path for display purposes.
    """
    if await files_are_identical(src, dst):
        if verbose:
            display_path = rel_path if rel_path else dst.name
            click.echo(f"  {display_path} (up to date)")
        return  # Skip identical files

    if await dst.exists() and not auto_yes:
        if not await prompt_user_confirmation(dst):
            if verbose:
                display_path = rel_path if rel_path else dst.name
                click.echo(f"  {display_path} (skipped)")
            return  # User declined overwrite

    # Copy the file with metadata
    if verbose:
        display_path = rel_path if rel_path else dst.name
        click.echo(f"  {display_path} (updated)")
    await aioshutil.copy2(str(src), str(dst))


async def make_executable(file_path: AsyncPath, verbose: bool = False) -> None:
    """Set executable permissions on file.

    Adds user, group, and other execute permissions to the file.

    Args:
        file_path: Path to file to make executable.
        verbose: If True, print detailed progress messages.
    """
    current_stat = await file_path.stat()
    await file_path.chmod(current_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


async def copy_directory(
    src: AsyncPath,
    dst: AsyncPath,
    auto_yes: bool,
    make_scripts_executable: bool = False,
    verbose: bool = False,
    base_path: AsyncPath | None = None,
) -> None:
    """Recursively copy directory with smart overwrite handling.

    Copies all files and subdirectories from src to dst. Optionally makes
    all copied files executable.

    Args:
        src: Source directory path.
        dst: Destination directory path.
        auto_yes: If True, skip confirmation prompts.
        make_scripts_executable: If True, make all copied files executable.
        verbose: If True, print detailed progress messages.
        base_path: Base path for computing relative paths (for display).

    Raises:
        FileNotFoundError: If source directory does not exist.
    """
    if not await src.exists():
        raise FileNotFoundError(f"Source directory {src} does not exist")

    if base_path is None:
        base_path = dst

    await dst.mkdir(parents=True, exist_ok=True)

    async for item in src.iterdir():
        src_item = src / item.name
        dst_item = dst / item.name

        if await src_item.is_dir():
            await copy_directory(src_item, dst_item, auto_yes, make_scripts_executable, verbose, base_path)
        else:
            # Compute relative path from base
            try:
                rel_path = str(dst_item.relative_to(base_path))
            except ValueError:
                rel_path = str(dst_item)

            await copy_file_if_needed(src_item, dst_item, auto_yes, verbose, rel_path)
            if make_scripts_executable:
                await make_executable(dst_item, verbose)


async def cli_main(auto_yes: bool, verbose: bool) -> None:
    """Main async entry point for Kiro installation.

    Performs the following steps:
    1. Checks if kiro-cli is installed
    2. Creates ~/.kiro directory structure
    3. Copies agents from kiro/agents to ~/.kiro/agents
    4. Copies scripts from kiro/scripts to ~/.kiro/scripts (making them executable)

    Args:
        auto_yes: If True, skip all confirmation prompts.
        verbose: If True, print detailed progress messages.

    Raises:
        SystemExit: If kiro-cli not found or source directories missing.
    """
    if not check_kiro_cli_installed():
        click.echo(
            "Error: kiro-cli not found in PATH. Please install kiro-cli first.",
            err=True,
        )
        sys.exit(1)

    click.echo("Setting up ~/.kiro directory structure...")
    home = await AsyncPath.home()
    base_path = home / ".kiro"
    await create_directories(base_path, verbose)
    click.echo("✓ Directories created")

    # Find source directories (relative to this script in src/)
    script_dir = AsyncPath(__file__).parent
    kiro_src = script_dir.parent / "kiro"

    if not await kiro_src.exists():
        click.echo(f"Error: Source directory {kiro_src} not found", err=True)
        sys.exit(1)

    # Copy agents directory
    agents_src = kiro_src / "agents"
    if await agents_src.exists():
        click.echo("Copying agents...")
        await copy_directory(
            agents_src,
            base_path / "agents",
            auto_yes,
            make_scripts_executable=False,
            verbose=verbose,
        )
        click.echo("✓ Agents copied")

    # Copy scripts directory
    scripts_src = kiro_src / "scripts"
    if await scripts_src.exists():
        click.echo("Copying scripts...")
        await copy_directory(
            scripts_src,
            base_path / "scripts",
            auto_yes,
            make_scripts_executable=True,
            verbose=verbose,
        )
        click.echo("✓ Scripts copied and made executable")

    click.echo("\n✅ Installation complete!")
    click.echo(f"Kiro files installed to: {base_path}")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--yes", "-y", "auto_yes", is_flag=True, help="Auto-confirm all prompts")
@click.option("--verbose", "-v", "verbose", is_flag=True, help="Show detailed progress messages")
def main(auto_yes: bool, verbose: bool) -> None:
    """Install Kiro configuration files and scripts to ~/.kiro.

    This command installs Kiro agents and scripts to your home directory,
    creating the necessary directory structure and making scripts executable.

    Args:
        auto_yes: If True, automatically confirm all file overwrites.
        verbose: If True, show detailed progress messages.
    """
    asyncio.run(cli_main(auto_yes, verbose))
