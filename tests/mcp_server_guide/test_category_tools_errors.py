"""Tests for category_tools.py error handling and edge cases."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from mcp_server_guide.tools.category_tools import _safe_glob_search, add_category, get_category_content


class TestSafeGlobSearchErrors:
    """Test error handling in _safe_glob_search function."""

    def test_symlink_resolution_error(self):
        """Test OSError handling in symlink resolution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            search_dir = Path(temp_dir)

            # Create a regular file
            test_file = search_dir / "test.md"
            test_file.write_text("content")

            # Mock Path.resolve to raise OSError
            with patch.object(Path, "resolve") as mock_resolve:
                mock_resolve.side_effect = OSError("Permission denied")

                with patch("mcp_server_guide.tools.category_tools.logger") as mock_logger:
                    _safe_glob_search(search_dir, ["*.md"])

                    # Should log warning and continue
                    mock_logger.warning.assert_called()
                    assert "Failed to resolve symlink" in mock_logger.warning.call_args[0][0]

    def test_glob_pattern_exception(self):
        """Test exception handling in glob operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            search_dir = Path(temp_dir)

            # Mock glob.iglob to raise exception
            with patch("glob.iglob") as mock_glob:
                mock_glob.side_effect = Exception("Glob error")

                with patch("mcp_server_guide.tools.category_tools.logger") as mock_logger:
                    result = _safe_glob_search(search_dir, ["*.md"])

                    # Should log warning and return empty list
                    mock_logger.warning.assert_called()
                    assert "Glob pattern" in mock_logger.warning.call_args[0][0]
                    assert "failed" in mock_logger.warning.call_args[0][0]
                    assert result == []


class TestAddCategoryErrors:
    """Test error handling in add_category function."""

    # Note: Configuration validation tests removed as validation is now handled by Pydantic models

    @pytest.mark.asyncio
    async def test_duplicate_category_error(self):
        """Test duplicate category name error."""
        from mcp_server_guide.project_config import ProjectConfig
        from mcp_server_guide.models.category import Category

        category_config = {"dir": "test", "patterns": ["*.md"], "description": "Test category"}

        # Mock SessionManager and session_state properly
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_current_project_safe = Mock(return_value="test_project")
            mock_session.get_project_name = Mock(return_value="test_project")

            # Create ProjectConfig with existing category
            config_data = ProjectConfig(
                categories={"test_cat": Category(dir="existing", patterns=["*.txt"], description="")}
            )
            mock_session.session_state.get_project_config = Mock(return_value=config_data)

            async def mock_get_config(project=None):
                return config_data

            mock_session.get_or_create_project_config = mock_get_config
            mock_session.session_state.set_project_config = Mock()

            async def mock_save():
                pass

            mock_session.save_session = mock_save
            mock_session_class.return_value = mock_session

            result = await add_category("test_cat", **category_config)

            assert result["success"] is False
            assert "Category 'test_cat' already exists" in result["error"]


class TestGetCategoryContentErrors:
    """Test error handling in get_category_content function."""

    @pytest.mark.asyncio
    async def test_no_patterns_defined(self):
        """Test error when category has no patterns."""
        from mcp_server_guide.project_config import ProjectConfig
        from mcp_server_guide.models.category import Category

        # Mock SessionManager properly
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_current_project_safe = Mock(return_value="test_project")
            mock_session.get_project_name = Mock(return_value="test_project")

            # Create ProjectConfig with category that has no patterns
            config_data = ProjectConfig(categories={"test_cat": Category(dir="test", patterns=None, description="")})

            async def mock_get_config(project=None):
                return config_data

            mock_session.get_or_create_project_config = mock_get_config
            mock_session_class.return_value = mock_session

            result = await get_category_content("test_cat")

            assert result["success"] is False
            assert "has no patterns defined" in result["error"]

    @pytest.mark.asyncio
    async def test_empty_patterns_list(self):
        """Test error when category has empty patterns list."""
        from mcp_server_guide.project_config import ProjectConfig
        from mcp_server_guide.models.category import Category

        # Mock SessionManager properly
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_current_project_safe = Mock(return_value="test_project")
            mock_session.get_project_name = Mock(return_value="test_project")

            # Create ProjectConfig with category that has empty patterns list
            config_data = ProjectConfig(categories={"test_cat": Category(dir="test", patterns=[], description="")})

            async def mock_get_config(project=None):
                return config_data

            mock_session.get_or_create_project_config = mock_get_config
            mock_session_class.return_value = mock_session

            result = await get_category_content("test_cat")

            assert result["success"] is False
            assert "has no patterns defined" in result["error"]

    @pytest.mark.asyncio
    async def test_category_directory_not_exists(self):
        """Test error when category directory doesn't exist."""
        from mcp_server_guide.path_resolver import LazyPath
        from mcp_server_guide.project_config import ProjectConfig
        from mcp_server_guide.models.category import Category

        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock SessionManager properly
            with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
                mock_session = Mock()
                mock_session.get_current_project_safe = Mock(return_value="test_project")
                mock_session.get_project_name = Mock(return_value="test_project")

                # Create ProjectConfig with nonexistent directory
                config_data = ProjectConfig(
                    categories={"test_cat": Category(dir="nonexistent", patterns=["*.md"], description="")}
                )

                async def mock_get_config(project=None):
                    return config_data

                mock_session.get_or_create_project_config = mock_get_config
                # Mock config_manager().docroot
                mock_config_manager = Mock()
                mock_config_manager.docroot = LazyPath(temp_dir)
                mock_session.config_manager = Mock(return_value=mock_config_manager)

                mock_session_class.return_value = mock_session

                result = await get_category_content("test_cat")

                assert result["success"] is False
                assert "does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_file_read_error(self):
        """Test error handling when file reading fails."""
        from mcp_server_guide.path_resolver import LazyPath

        with tempfile.TemporaryDirectory() as temp_dir:
            search_dir = Path(temp_dir) / "test"
            search_dir.mkdir()

            # Create a test file
            test_file = search_dir / "test.md"
            test_file.write_text("test content")

            # Mock SessionManager properly
            with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
                mock_session = Mock()
                mock_session.get_current_project_safe = Mock(return_value="test_project")
                mock_session.get_project_name = Mock(return_value="test_project")

                # Create ProjectConfig
                from mcp_server_guide.project_config import ProjectConfig
                from mcp_server_guide.models.category import Category

                config_data = ProjectConfig(
                    categories={"test_cat": Category(dir="test", patterns=["*.md"], description="")}
                )

                async def mock_get_config(project=None):
                    return config_data

                mock_session.get_or_create_project_config = mock_get_config
                # Mock config_manager().docroot
                mock_config_manager = Mock()
                mock_config_manager.docroot = LazyPath(temp_dir)
                mock_session.config_manager = Mock(return_value=mock_config_manager)

                mock_session_class.return_value = mock_session

                # Mock aiofiles.open to raise exception
                with patch("aiofiles.open") as mock_open:
                    mock_open.side_effect = Exception("Permission denied")

                    result = await get_category_content("test_cat")

                    assert result["success"] is True
                    assert "Error reading file" in result["content"]

    @pytest.mark.asyncio
    async def test_partial_file_read_failure(self):
        """Test handling when multiple files exist and some fail to read."""
        from mcp_server_guide.path_resolver import LazyPath

        with tempfile.TemporaryDirectory() as temp_dir:
            search_dir = Path(temp_dir) / "test"
            search_dir.mkdir()

            # Create multiple test files
            file1 = search_dir / "file1.md"
            file1.write_text("content1")
            file2 = search_dir / "file2.md"
            file2.write_text("content2")

            with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
                mock_session = Mock()
                mock_session.get_current_project_safe = Mock(return_value="test_project")
                mock_session.get_project_name = Mock(return_value="test_project")
                # Create ProjectConfig
                from mcp_server_guide.project_config import ProjectConfig
                from mcp_server_guide.models.category import Category

                config_data = ProjectConfig(
                    categories={"test_cat": Category(dir="test", patterns=["*.md"], description="")}
                )

                async def mock_get_config(project=None):
                    return config_data

                mock_session.get_or_create_project_config = mock_get_config
                # Mock config_manager().docroot
                mock_config_manager = Mock()
                mock_config_manager.docroot = LazyPath(temp_dir)
                mock_session.config_manager = Mock(return_value=mock_config_manager)

                mock_session_class.return_value = mock_session

                # Mock aiofiles.open to always fail
                with patch("aiofiles.open") as mock_open:
                    mock_open.side_effect = Exception("Permission denied")

                    result = await get_category_content("test_cat")

                    assert result["success"] is True
                    # Should have error messages for both files
                    assert result["content"].count("Error reading file") == 2
                    assert "file1.md" in result["content"]
                    assert "file2.md" in result["content"]

    @pytest.mark.asyncio
    async def test_no_matching_files(self):
        """Test when no files match the patterns."""
        from mcp_server_guide.path_resolver import LazyPath

        with tempfile.TemporaryDirectory() as temp_dir:
            search_dir = Path(temp_dir) / "test"
            search_dir.mkdir()

            # Mock SessionManager properly
            with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
                mock_session = Mock()
                mock_session.get_current_project_safe = Mock(return_value="test_project")
                mock_session.get_project_name = Mock(return_value="test_project")

                # Create ProjectConfig
                from mcp_server_guide.project_config import ProjectConfig
                from mcp_server_guide.models.category import Category

                config_data = ProjectConfig(
                    categories={"test_cat": Category(dir="test", patterns=["*.nonexistent"], description="")}
                )

                async def mock_get_config(project=None):
                    return config_data

                mock_session.get_or_create_project_config = mock_get_config
                # Mock config_manager().docroot
                mock_config_manager = Mock()
                mock_config_manager.docroot = LazyPath(temp_dir)
                mock_session.config_manager = Mock(return_value=mock_config_manager)

                mock_session_class.return_value = mock_session

                result = await get_category_content("test_cat")

                assert result["success"] is True
                assert result["content"] == ""
                assert "No files found" in result["message"]
