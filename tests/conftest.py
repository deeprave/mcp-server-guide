"""Test configuration and fixtures for proper isolation."""

import tempfile
import os
from pathlib import Path
from typing import Generator
import pytest

from mcp_server_guide.session_tools import SessionManager


@pytest.fixture(autouse=True)
def complete_test_isolation():
    """Ensure complete test isolation - no modification of project files."""
    # Store original working directory
    original_cwd = os.getcwd()

    # Reset SessionManager singleton
    SessionManager._instance = None

    # Create isolated temp directory for each test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory to prevent any file creation in project root
        os.chdir(temp_dir)

        try:
            yield temp_dir
        finally:
            # Always restore original directory and reset singleton
            os.chdir(original_cwd)
            SessionManager._instance = None


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Provide temporary project directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
