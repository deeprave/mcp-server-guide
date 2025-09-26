"""Test configuration and fixtures for proper isolation."""

import tempfile
import os
from pathlib import Path
from typing import Generator
import pytest

from mcp_server_guide.session_tools import SessionManager


@pytest.fixture(autouse=True)
def reset_session_manager():
    """Reset SessionManager singleton before each test."""
    SessionManager._instance = None
    yield
    SessionManager._instance = None


@pytest.fixture
def isolated_config() -> Generator[str, None, None]:
    """Provide isolated configuration file for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_dir)
            config_filename = "test-config.json"
            yield config_filename
        finally:
            os.chdir(original_cwd)


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Provide temporary project directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
