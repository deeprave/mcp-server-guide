"""Centralized installation utilities to avoid code duplication."""

import contextlib
from pathlib import Path

import aioshutil


def get_templates_dir() -> Path:
    """Get the templates directory from the installed package (synchronous).

    Returns:
        Path to the templates directory

    Raises:
        FileNotFoundError: If templates directory can't be found
    """
    # Primary: templates relative to this module (development/installed package)
    script_dir = Path(__file__).parent
    package_templates = script_dir.parent.parent.parent / "templates"

    if package_templates.exists():
        return package_templates

    # Fallback: package installation directory
    with contextlib.suppress(ImportError):
        import mcp_server_guide

        package_dir = Path(mcp_server_guide.__file__).parent
        fallback_templates = package_dir.parent / "templates"
        if fallback_templates.exists():
            return fallback_templates

    raise FileNotFoundError(
        "Templates directory not found. This may indicate an incomplete installation. "
        "Please ensure mcp-server-guide is properly installed."
    )


async def copy_item(src_item: Path, dst_item: Path) -> None:
    """Copy a single file or directory silently using async operations.

    Args:
        src_item: Source path (file or directory)
        dst_item: Destination path

    Raises:
        FileNotFoundError: If the source doesn't exist
        IOError: If the copy operation fails
    """
    if src_item.is_dir():
        if dst_item.exists() and not dst_item.is_dir():
            dst_item.unlink()
        dst_item.mkdir(parents=True, exist_ok=True)
        for child in src_item.iterdir():
            if child.name.startswith("."):
                continue
            await copy_item(child, dst_item / child.name)
    else:
        if dst_item.exists() and dst_item.is_dir():
            await aioshutil.rmtree(dst_item, ignore_errors=False)  # type: ignore
        dst_item.parent.mkdir(parents=True, exist_ok=True)
        await aioshutil.copy2(src_item, dst_item)


async def copy_templates(source: Path, destination: Path) -> None:
    """Copy templates from source to destination without user interaction.

    Args:
        source: Source templates directory
        destination: Destination path

    Raises:
        FileNotFoundError: If the source file doesn't exist.
        IOError: If the copy operation fails
    """
    if not source.exists():
        raise FileNotFoundError(f"Source templates directory not found: {source}")

    destination.mkdir(parents=True, exist_ok=True)

    for item in source.iterdir():
        if item.name.startswith("."):
            continue
        await copy_item(item, destination / item.name)
