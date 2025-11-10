"""Test configuration and fixtures for proper isolation."""

import tempfile
import os
import shutil
import atexit
import asyncio
from pathlib import Path
from typing import Generator, Union
import pytest

from mcp_server_guide.session_manager import SessionManager


# Global session temp directory
_session_temp_dir: Path | None = None


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config_filename(monkeypatch):
    """Mock config filename to use test directory.

    DEPRECATED: Use isolated_config_file fixture instead for tests that need real file I/O.
    This fixture is only for tests that don't actually read/write config files.
    """

    # noinspection PyUnusedLocal
    def mock_getter(self):
        return os.path.join(os.getcwd(), "config.yaml")

    from mcp_server_guide.project_config import ProjectConfigManager

    monkeypatch.setattr(ProjectConfigManager, "get_config_filename", mock_getter)


@pytest.fixture
def isolated_config_file():
    """Provide an isolated config file path for tests that need real file I/O.

    Tests that read/write config files should use this fixture and call:
        SessionManager()._set_config_filename(isolated_config_file)

    This ensures tests use a test-local file instead of the global config.
    """
    config_path = Path(os.getcwd()) / "test_config.yaml"

    # Clean up any existing file
    if config_path.exists():
        config_path.unlink()

    yield config_path

    # Cleanup after test
    if config_path.exists():
        config_path.unlink()


@pytest.fixture
def chdir():
    """Fixture that provides a chdir function that updates both cwd and PWD."""

    def _chdir(path: Union[str, Path]) -> None:
        """Change directory and update PWD environment variable."""
        os.chdir(path)
        os.environ["PWD"] = os.getcwd()

    return _chdir


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


# pytest hooks for session setup/teardown


# noinspection PyUnusedLocal
def pytest_sessionstart(session):
    """Create the session-scoped temp directory."""
    global _session_temp_dir
    _session_temp_dir = Path(tempfile.mkdtemp(prefix="mcp_test_session_"))

    # Register cleanup to run even if pytest crashes
    atexit.register(lambda: robust_cleanup(_session_temp_dir))


# noinspection PyUnusedLocal
def pytest_sessionfinish(session, exitstatus):
    """Clean up the session-scoped temp directory."""
    global _session_temp_dir
    if _session_temp_dir:
        robust_cleanup(_session_temp_dir)


@pytest.fixture(autouse=True)
def complete_test_isolation(request, monkeypatch):
    """Ensure complete test isolation - no modification of project files."""
    global _session_temp_dir

    # Store original working directory and PWD
    original_cwd = os.getcwd()
    original_pwd = os.environ.get("PWD")

    # Reset SessionManager singleton
    SessionManager.clear()

    # Create unique subdirectory for this test within session temp dir
    test_name = request.node.name
    test_subdir = _session_temp_dir / f"test_{test_name}_{id(request)}"
    test_subdir.mkdir(parents=True, exist_ok=True)

    # Change to test subdirectory and update PWD
    os.chdir(test_subdir)
    os.environ["PWD"] = str(test_subdir)

    # No need to mock ClientPath since it's been removed
    # PWD-based project detection will handle directory context

    try:
        yield str(test_subdir)
    finally:
        # Always restore original directory and PWD
        os.chdir(original_cwd)
        if original_pwd is not None:
            os.environ["PWD"] = original_pwd
        elif "PWD" in os.environ:
            del os.environ["PWD"]
        SessionManager.clear()


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
