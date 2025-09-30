"""Test configuration and fixtures for proper isolation."""

import tempfile
import os
import shutil
import atexit
from pathlib import Path
from typing import Generator
import pytest

from mcp_server_guide.session_tools import SessionManager

# Global session temp directory
_session_temp_dir = None


def robust_cleanup(directory: Path) -> None:
    """Robustly clean up a directory, handling read-only files and other issues."""

    def handle_remove_readonly(func, path, _exc):
        """Error handler for shutil.rmtree to handle read-only files."""
        import stat

        if os.path.exists(path):
            # Make the file writable and try again
            os.chmod(path, stat.S_IWRITE)
            func(path)

    if directory.exists():
        shutil.rmtree(directory, onerror=handle_remove_readonly)


def pytest_sessionstart(session):
    """Create session-scoped temp directory."""
    global _session_temp_dir
    _session_temp_dir = Path(tempfile.mkdtemp(prefix="mcp_test_session_"))

    # Register cleanup to run even if pytest crashes
    atexit.register(lambda: robust_cleanup(_session_temp_dir))


def pytest_sessionfinish(session, exitstatus):
    """Clean up session-scoped temp directory."""
    global _session_temp_dir
    if _session_temp_dir:
        robust_cleanup(_session_temp_dir)


@pytest.fixture(autouse=True)
def complete_test_isolation(request):
    """Ensure complete test isolation - no modification of project files."""
    global _session_temp_dir

    # Store original working directory
    original_cwd = os.getcwd()

    # Reset SessionManager singleton
    SessionManager._instance = None

    # Create unique subdirectory for this test within session temp dir
    test_name = request.node.name
    test_subdir = _session_temp_dir / f"test_{test_name}_{id(request)}"
    test_subdir.mkdir(parents=True, exist_ok=True)

    # Change to test subdirectory
    os.chdir(test_subdir)

    try:
        yield str(test_subdir)
    finally:
        # Always restore original directory and reset singleton
        os.chdir(original_cwd)
        SessionManager._instance = None


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Provide temporary project directory for tests."""
    import uuid

    global _session_temp_dir

    # Create subdirectory within session temp dir
    project_subdir = _session_temp_dir / f"project_{uuid.uuid4().hex[:8]}"
    project_subdir.mkdir(parents=True, exist_ok=True)

    yield project_subdir


# Make session temp dir available to tests
@pytest.fixture
def session_temp_dir() -> Path:
    """Provide access to session temp directory."""
    global _session_temp_dir
    return _session_temp_dir
