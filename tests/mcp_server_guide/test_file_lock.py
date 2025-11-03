"""Tests for file locking strategy."""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from mcp_server_guide.file_lock import lock_update, is_process_running


async def test_lock_update_creates_lock_file():
    """Test that lock_update creates a lock file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"

        def dummy_func(file_path):
            return "success"

        result = lock_update(config_file, dummy_func)

        assert result == "success"
        # Lock file should be cleaned up after execution
        lock_file = config_file.with_suffix(config_file.suffix + ".lock")
        assert not lock_file.exists()


async def test_lock_file_contains_hostname_and_pid():
    """Test that lock file contains hostname:pid format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"
        lock_file = config_file.with_suffix(config_file.suffix + ".lock")

        def check_lock_content(file_path):
            # Check lock file content while it exists
            with open(lock_file, "r") as f:
                content = f.read().strip()

            parts = content.split(":")
            assert len(parts) == 2
            hostname, pid_str = parts

            # Verify hostname is not empty and matches expected format
            assert hostname != ""
            assert "." not in hostname  # Should be short hostname

            # Verify pid is current process
            assert pid_str == str(os.getpid())

            return "success"

        result = lock_update(config_file, check_lock_content)
        assert result == "success"


async def test_lock_update_executes_function_with_args():
    """Test that lock_update executes function with args and kwargs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"

        def test_func(file_path, arg1, arg2, kwarg1=None, kwarg2=None):
            return {"file_path": str(file_path), "arg1": arg1, "arg2": arg2, "kwarg1": kwarg1, "kwarg2": kwarg2}

        result = lock_update(config_file, test_func, "value1", "value2", kwarg1="kw1", kwarg2="kw2")

        expected = {"file_path": str(config_file), "arg1": "value1", "arg2": "value2", "kwarg1": "kw1", "kwarg2": "kw2"}
        assert result == expected


async def test_lock_file_removed_after_successful_execution():
    """Test that lock file is removed after successful execution."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"
        lock_file = config_file.with_suffix(config_file.suffix + ".lock")

        lock_existed_during_execution = False

        def check_lock_exists(file_path):
            nonlocal lock_existed_during_execution
            lock_existed_during_execution = lock_file.exists()
            return "completed"

        result = lock_update(config_file, check_lock_exists)

        # Lock should have existed during execution
        assert lock_existed_during_execution
        # Lock should be removed after execution
        assert not lock_file.exists()
        assert result == "completed"


async def test_lock_file_removed_after_exception():
    """Test that lock file is removed even when function raises exception."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"
        lock_file = config_file.with_suffix(config_file.suffix + ".lock")

        def failing_func(file_path):
            # Verify lock exists during execution
            assert lock_file.exists()
            raise ValueError("Test exception")

        with pytest.raises(ValueError, match="Test exception"):
            lock_update(config_file, failing_func)

        # Lock should be removed even after exception
        assert not lock_file.exists()


async def test_is_process_running_detects_live_process():
    """Test that is_process_running detects live process."""
    # Current process should be running
    current_pid = os.getpid()
    assert is_process_running(current_pid) is True


async def test_is_process_running_detects_dead_process():
    """Test that is_process_running detects dead process."""
    # Use a very high PID that's unlikely to exist
    fake_pid = 999999
    assert is_process_running(fake_pid) is False


async def test_stale_lock_different_hostname_dead_process():
    """Test that stale lock is detected for different hostname with dead process."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"
        lock_file = config_file.with_suffix(config_file.suffix + ".lock")

        # Create a stale lock file with different hostname and dead PID
        with open(lock_file, "w") as f:
            f.write("different-host:999999")

        def dummy_func(file_path):
            return "success"

        # Should succeed by removing stale lock
        result = lock_update(config_file, dummy_func)
        assert result == "success"


async def test_project_config_save_uses_locking():
    """Test that ProjectConfigManager.save_config uses locking."""
    from mcp_server_guide.project_config import ProjectConfigManager, ProjectConfig
    from mcp_server_guide.models.category import Category

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        config = ProjectConfig(categories={"test": Category(dir="test/", patterns=["*.md"])})

        manager = ProjectConfigManager()
        # Set config file to temp directory to avoid overwriting actual config
        manager.set_config_filename(project_path / "test_config.yaml")

        # This should use locking internally
        manager.save_config("test-project", config)

        # Verify config was saved to temp location
        config_file = Path(manager.get_config_filename())
        assert config_file.exists()

        # Verify no lock file remains
        lock_file = config_file.with_suffix(config_file.suffix + ".lock")
        assert not lock_file.exists()
    """Test that stale lock is detected for old mtime."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"
        lock_file = config_file.with_suffix(config_file.suffix + ".lock")

        # Create a lock file with current hostname and PID but old mtime
        current_hostname = os.uname().nodename.split(".")[0]
        current_pid = os.getpid()
        with open(lock_file, "w") as f:
            f.write(f"{current_hostname}:{current_pid}")

        # Mock the mtime to be old (>10 minutes)
        old_time = time.time() - 700  # 11+ minutes ago
        with patch("os.path.getmtime", return_value=old_time):

            def dummy_func(file_path):
                return "success"

            # Should succeed by removing stale lock
            result = lock_update(config_file, dummy_func)
            assert result == "success"


async def test_concurrent_config_updates_prevented():
    """Test that concurrent configuration updates are prevented by locking."""
    import threading
    from mcp_server_guide.project_config import ProjectConfigManager, ProjectConfig
    from mcp_server_guide.models.category import Category

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        manager = ProjectConfigManager()
        # Set config file to temp directory to avoid overwriting actual config
        manager.set_config_filename(project_path / "test_config.yaml")

        results = []

        def save_config(project_name):
            config = ProjectConfig(categories={"test": Category(dir="test/", patterns=["*.md"])})
            manager.save_config(project_name, config)
            results.append(project_name)

        # Start two concurrent saves
        thread1 = threading.Thread(target=save_config, args=("project1",))
        thread2 = threading.Thread(target=save_config, args=("project2",))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Both should complete successfully
        assert len(results) == 2
        assert "project1" in results
        assert "project2" in results

        # Final config should be one of them (last writer wins)
        config_file = Path(manager.get_config_filename())
        assert config_file.exists()

        # No lock file should remain
        lock_file = config_file.with_suffix(config_file.suffix + ".lock")
        assert not lock_file.exists()


async def test_invalid_lock_file_format_handled(tmp_path):
    """Test that invalid lock file format is handled gracefully."""
    config_file = tmp_path / "config.yaml"
    lock_file = tmp_path / "config.yaml.lock"  # Match the file_path suffix

    # Create lock file with invalid format
    lock_file.write_text("invalid-format")

    def test_func(file_path):
        return "success"

    # Should treat invalid format as stale and remove it
    result = lock_update(config_file, test_func)

    assert result == "success"
    assert not lock_file.exists()


async def test_lock_file_read_errors_handled(tmp_path, monkeypatch):
    """Test that lock file read errors are handled gracefully."""
    config_file = tmp_path / "config.yaml"
    lock_file = tmp_path / "config.json.lock"

    # Create lock file
    lock_file.write_text("host:123")

    # Mock pathlib.Path.read_text to raise an exception
    def mock_read_text(*args, **kwargs):
        raise PermissionError("Cannot read lock file")

    monkeypatch.setattr("pathlib.Path.read_text", mock_read_text)

    def test_func(file_path):
        return "success"

    # Should handle read error and proceed (treating as no lock)
    result = lock_update(config_file, test_func)

    assert result == "success"
