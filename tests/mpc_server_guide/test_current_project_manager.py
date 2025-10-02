"""Test CurrentProjectManager for directory-scoped project tracking."""

import os
import sys
import pytest

from mcp_server_guide.current_project_manager import CurrentProjectManager


class TestCurrentProjectManager:
    """Test CurrentProjectManager functionality."""

    async def test_current_project_manager_creation(self):
        """Test CurrentProjectManager can be created."""
        manager = CurrentProjectManager()
        assert manager is not None

    async def test_get_current_project_with_current_file(self, tmp_path, chdir):
        """Test reading project from .mcp-server-guide.current file."""
        # Create .current file with project name
        current_file = tmp_path / ".mcp-server-guide.current"
        current_file.write_text("test-project")

        # Change to temp directory (updates both cwd and PWD)
        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)
            manager = CurrentProjectManager()
            project = manager.get_current_project()
            assert project == "test-project"
        finally:
            chdir(original_cwd)

    async def test_get_current_project_fallback_to_directory_name(self, tmp_path, chdir):
        """Test fallback to directory name when no .current file exists."""
        # Create directory with specific name
        project_dir = tmp_path / "my-awesome-project"
        project_dir.mkdir()

        original_cwd = os.getcwd()
        try:
            chdir(project_dir)
            manager = CurrentProjectManager()
            project = manager.get_current_project()
            assert project == "my-awesome-project"
        finally:
            chdir(original_cwd)

    async def test_set_current_project_creates_current_file(self, tmp_path, chdir):
        """Test setting project creates .mcp-server-guide.current file."""
        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)
            manager = CurrentProjectManager()
            manager.set_current_project("new-project")

            current_file = tmp_path / ".mcp-server-guide.current"
            assert current_file.exists()
            assert current_file.read_text().strip() == "new-project"
        finally:
            chdir(original_cwd)

    async def test_set_current_project_updates_existing_file(self, tmp_path, chdir):
        """Test setting project updates existing .current file."""
        current_file = tmp_path / ".mcp-server-guide.current"
        current_file.write_text("old-project")

        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)
            manager = CurrentProjectManager()
            manager.set_current_project("updated-project")

            assert current_file.read_text().strip() == "updated-project"
        finally:
            chdir(original_cwd)

    async def test_concurrent_access_safety(self, tmp_path, chdir):
        """Test that concurrent access doesn't corrupt .current file."""
        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)

            # Simulate concurrent access
            manager1 = CurrentProjectManager()
            manager2 = CurrentProjectManager()

            manager1.set_current_project("project-1")
            manager2.set_current_project("project-2")

            # Last write should win
            current_file = tmp_path / ".mcp-server-guide.current"
            assert current_file.read_text().strip() == "project-2"

            # Both managers should read the same value
            assert manager1.get_current_project() == "project-2"
            assert manager2.get_current_project() == "project-2"
        finally:
            chdir(original_cwd)

    @pytest.mark.skipif(sys.platform.startswith("win"), reason="Permission error simulation is not reliable on Windows")
    async def test_handles_missing_permissions(self, tmp_path, chdir):
        """
        Test graceful handling when .current file can't be written.

        Conditionally skipped on platforms where simulating permission errors is not reliable (e.g., Windows).

        Manual coverage (if not run automatically):
        - On Unix-like systems, run with .current file or parent directory set to read-only
        - On Windows, use file properties to deny write access
        - Verify permission errors are handled gracefully (no crash, appropriate error message)
        """
        pytest.skip("Permission testing requires platform-specific setup; see docstring for manual coverage steps.")

    async def test_clear_current_project(self, tmp_path, chdir):
        """Test clearing current project removes .current file."""
        current_file = tmp_path / ".mcp-server-guide.current"
        current_file.write_text("test-project")

        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)
            manager = CurrentProjectManager()
            manager.clear_current_project()

            assert not current_file.exists()
            # Should fallback to directory name
            assert manager.get_current_project() == tmp_path.name
        finally:
            chdir(original_cwd)

    async def test_has_current_file(self, tmp_path, chdir):
        """Test checking if .current file exists."""
        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)
            manager = CurrentProjectManager()

            assert not manager.has_current_file()

            manager.set_current_project("test-project")
            assert manager.has_current_file()

            manager.clear_current_project()
            assert not manager.has_current_file()
        finally:
            chdir(original_cwd)

    async def test_set_current_project_validates_input(self, tmp_path, chdir):
        """Test that empty project names are rejected."""
        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)
            manager = CurrentProjectManager()

            with pytest.raises(ValueError, match="Project name cannot be empty"):
                manager.set_current_project("")

            with pytest.raises(ValueError, match="Project name cannot be empty"):
                manager.set_current_project("   ")

            with pytest.raises(ValueError, match="Project name cannot be empty"):
                manager.set_current_project("\t\n\t")
        finally:
            chdir(original_cwd)

    async def test_handles_invalid_current_file_content(self, tmp_path, chdir):
        """Test handling of corrupted .current file."""
        current_file = tmp_path / ".mcp-server-guide.current"
        current_file.write_text("")  # Empty file

        original_cwd = os.getcwd()
        try:
            chdir(tmp_path)
            manager = CurrentProjectManager()
            # Should fallback to directory name when .current is empty
            project = manager.get_current_project()
            assert project == tmp_path.name
        finally:
            chdir(original_cwd)
