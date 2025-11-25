"""Test configuration and fixtures for proper isolation."""

import asyncio
import atexit
import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Union
from unittest.mock import Mock

import pytest
from mcp.server.fastmcp import Context

from mcp_server_guide.session_manager import SessionManager

# Global session temp directory
_session_temp_dir: Path | None = None


def pytest_configure(config):
    """Configure pytest - runs BEFORE any test collection or imports.

    This is the ONLY way to ensure environment variables are set before
    any code imports and caches paths.
    """
    global _session_temp_dir

    # Create session-wide temp directory
    _session_temp_dir = Path(tempfile.mkdtemp(prefix="mcp_test_session_"))

    # Create isolated config and docs directories
    test_config_dir = _session_temp_dir / "config"
    test_docs_dir = _session_temp_dir / "docs"
    test_config_dir.mkdir(parents=True)
    test_docs_dir.mkdir(parents=True)

    # Create mcp-server-guide subdirectory for config files
    (test_config_dir / "mcp-server-guide").mkdir(parents=True, exist_ok=True)

    # Override environment variables BEFORE any imports
    os.environ["HOME"] = str(_session_temp_dir)
    os.environ["XDG_CONFIG_HOME"] = str(test_config_dir)
    os.environ["XDG_DATA_HOME"] = str(test_docs_dir)

    # Windows support
    if os.name == "nt":
        os.environ["APPDATA"] = str(test_config_dir)
        os.environ["LOCALAPPDATA"] = str(test_config_dir)


def pytest_unconfigure(config):
    """Cleanup after all tests complete."""
    global _session_temp_dir

    if _session_temp_dir:
        robust_cleanup(_session_temp_dir)
        _session_temp_dir = None


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def unique_category_name(request):
    """Generate a unique category name for each test to prevent conflicts.

    Category names must be alphanumeric with hyphens/underscores and max 30 chars.
    """
    # Use hash of test node ID to create short unique name
    test_id = request.node.nodeid
    hash_val = hashlib.md5(test_id.encode()).hexdigest()[:8]
    return f"cat_{hash_val}"


@pytest.fixture(autouse=True)
def reset_singleton_before_test():
    """Reset SessionManager singleton before each test to prevent state leakage.

    This ensures every test starts with a fresh SessionManager instance.
    """
    import mcp_server_guide.session_manager as sm_module

    sm_module._session_manager_instance = None
    yield
    sm_module._session_manager_instance = None


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
def isolated_session_manager(isolated_config_file):
    """Provide a SessionManager with isolated config file.

    Note: Session-level isolation already ensures all paths are in temp directory.
    This fixture sets a unique config filename and resets the singleton for the test.
    """
    import mcp_server_guide.session_manager as sm_module

    # Reset singleton to get fresh instance
    sm_module._session_manager_instance = None

    manager = SessionManager()
    manager._set_config_filename(isolated_config_file)

    # Ensure config file directory exists
    isolated_config_file.parent.mkdir(parents=True, exist_ok=True)

    yield manager

    # Reset singleton after test
    sm_module._session_manager_instance = None


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


@pytest.fixture
def mock_context():
    """Create a mock MCP Context for testing."""
    if Context is None:
        pytest.skip("MCP Context not available for testing")

    ctx = Mock(spec=Context)
    ctx.session = Mock()

    # Default mock root pointing to current test directory
    mock_root = Mock()
    mock_root.uri = f"file://{Path.cwd()}"
    ctx.session.list_roots.return_value = [mock_root]

    return ctx


@pytest.fixture
def mock_context_with_project(mock_context):
    """Create a mock MCP Context with a specific project setup."""
    mock_root = Mock()
    mock_root.uri = "file:///home/user/test-project"
    mock_context.session.list_roots.return_value = [mock_root]
    return mock_context
