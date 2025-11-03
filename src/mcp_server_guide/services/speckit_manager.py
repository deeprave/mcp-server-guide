"""SpecKit management service."""

from typing import Dict, Any
from ..models.speckit_config import SpecKitConfig
from ..session_manager import SessionManager


def is_speckit_enabled() -> bool:
    """Check if SpecKit is enabled in the configuration.

    Returns:
        True if SpecKit is enabled, False otherwise
    """
    session = SessionManager()
    return session.is_speckit_enabled()


def get_speckit_config() -> SpecKitConfig:
    """Get current SpecKit configuration.

    Returns:
        SpecKitConfig instance (default if not configured)
    """
    session = SessionManager()
    config = session.get_speckit_config()
    if config is not None:
        return config
    return SpecKitConfig(enabled=False, url="https://github.com/spec-kit/spec-kit", version="latest")


def enable_speckit(url: str = "https://github.com/spec-kit/spec-kit", version: str = "latest") -> None:
    """Enable SpecKit with the given configuration.

    Args:
        url: GitHub repository URL
        version: Version to use
    """
    session = SessionManager()
    config = SpecKitConfig(enabled=True, url=url, version=version)
    session.set_speckit_config(config)


def update_speckit_config(updates: Dict[str, Any]) -> None:
    """Update SpecKit configuration with new values.

    Args:
        updates: Dictionary of configuration updates
    """
    session = SessionManager()
    current_config = session.get_speckit_config()

    if current_config is None:
        current_config = SpecKitConfig(enabled=False, url="https://github.com/spec-kit/spec-kit", version="latest")

    # Update with new values
    updated_config = current_config.model_copy(update=updates)
    session.set_speckit_config(updated_config)
