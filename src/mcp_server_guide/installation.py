"""Shared installation module for both auto-init and manual install."""

import yaml
from pathlib import Path

import aiofiles

from .utils.installation_utils import get_templates_dir, copy_templates
from .exceptions import ConfigurationError
from .models.config_file import get_default_docroot


async def auto_initialize_new_installation(config_file: Path) -> None:
    """Auto-initialize a new installation when config file doesn't exist.

    This function is called when we have exclusive access via file lock
    and know for certain this is a new installation.

    Only handles infrastructure setup:
    - Creates config file with docroot
    - Creates docroot directory
    - Copies templates

    Project config creation is handled by session manager.

    Args:
        config_file: Path to config file that doesn't exist
    """
    # Get default docroot - use relative to config file if in test environment
    default_docroot = get_default_docroot()
    if str(config_file).startswith("/tmp") or str(config_file).startswith("/var/folders"):
        # Test environment - use relative to config file
        docroot = config_file.parent / "docs"
    else:
        # Production environment - use global default
        docroot = Path(default_docroot).expanduser()

    # Create directories
    config_file.parent.mkdir(parents=True, exist_ok=True)
    docroot.mkdir(parents=True, exist_ok=True)

    # Copy templates using shared utility
    templates_dir = get_templates_dir()
    await copy_templates(templates_dir, docroot)

    # Create minimal config file with just docroot
    await create_default_config(config_file, docroot)


async def create_default_config(config_path: Path, docroot: Path) -> None:
    """Create a minimal configuration file with just docroot.

    Default categories will be created automatically by the session manager
    when the project is first accessed.

    Args:
        config_path: Path where to create the config file
        docroot: Path to the document root directory

    Raises:
        ConfigurationError: If config creation fails
    """
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {"docroot": str(docroot.resolve())}
        yaml_content = yaml.dump(config_data, default_flow_style=False, sort_keys=False)

        async with aiofiles.open(config_path, "w") as f:
            await f.write(yaml_content)

    except (OSError, yaml.YAMLError) as e:
        raise ConfigurationError(f"Failed to create config file: {e}") from e
