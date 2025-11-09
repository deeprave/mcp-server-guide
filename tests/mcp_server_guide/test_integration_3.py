"""Additional tests for content tools and search functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch, AsyncMock, Mock
from mcp_server_guide.tools.content_tools import search_content
from mcp_server_guide.tools.category_tools import get_category_content


async def test_search_content_with_matches():
    """Test search_content finds matching content."""
    # Mock get_category_content to return content with search term
    mock_results = {
        "guide": {"success": True, "content": "This contains the search term"},
        "lang": {"success": True, "content": "This does not contain it"},
        "context": {"success": True, "content": "Another search term match"},
    }

    with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_get:

        def side_effect(category):
            return mock_results.get(category, {"success": False})

        mock_get.side_effect = side_effect

        results = await search_content("search term", "test-project")

        # Should find matches in guide and context categories
        assert len(results) == 2
        assert any("guide" in str(result) for result in results)
        assert any("context" in str(result) for result in results)


async def test_search_content_no_matches():
    """Test search_content with no matches."""
    # Mock get_category_content to return content without search term
    mock_results = {
        "guide": {"success": True, "content": "No matching content here"},
        "lang": {"success": True, "content": "Different content"},
        "context": {"success": True, "content": "Also different"},
    }

    with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_get:

        def side_effect(category):
            return mock_results.get(category, {"success": False})

        mock_get.side_effect = side_effect

        results = await search_content("nonexistent", "test-project")

        # Should find no matches
        assert len(results) == 0


async def test_search_content_failed_category():
    """Test search_content handles failed category retrieval."""
    # Mock get_category_content to return failures
    with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_get:
        mock_get.return_value = {"success": False, "error": "Category not found"}

        results = await search_content("test", "test-project")

        # Should handle failures gracefully
        assert len(results) == 0


async def test_category_content_directory_not_exists():
    """Test get_category_content when directory doesn't exist."""
    from mcp_server_guide.path_resolver import LazyPath
    from mcp_server_guide.project_config import ProjectConfig
    from mcp_server_guide.models.category import Category

    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up session with non-existent directory
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session:
            mock_session.return_value.get_project_name = Mock(return_value="test-project")
            config_data = ProjectConfig(
                categories={"test": Category(dir="nonexistent/", patterns=["*.md"], description="Test category")}
            )
            mock_session.return_value.get_or_create_project_config = AsyncMock(return_value=config_data)
            # Mock config_manager().docroot
            mock_config_manager = Mock()
            mock_config_manager.docroot = LazyPath(temp_dir)
            mock_session.return_value.config_manager = Mock(return_value=mock_config_manager)

            result = await get_category_content("test")

            assert result["success"] is False
            assert "does not exist" in result["error"]


async def test_safe_glob_outside_search_directory():
    """Test safe glob handles files outside search directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        search_dir = base_path / "search"
        search_dir.mkdir()

        # Create file in search directory
        (search_dir / "inside.md").write_text("inside content")

        # Mock relative_to to raise ValueError (file outside directory)
        with patch("pathlib.Path.relative_to") as mock_relative:
            mock_relative.side_effect = ValueError("Path is outside")

            with patch("mcp_server_guide.tools.category_tools.logger") as mock_logger:
                from mcp_server_guide.tools.category_tools import _safe_glob_search

                results = _safe_glob_search(search_dir, ["*.md"])

                # Should skip files outside search directory
                assert len(results) == 0
                mock_logger.debug.assert_called()


async def test_safe_glob_depth_limit():
    """Test safe glob respects depth limit."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create nested structure beyond depth limit
        deep_path = base_path
        for i in range(10):  # More than MAX_GLOB_DEPTH
            deep_path = deep_path / f"level{i}"
            deep_path.mkdir()

        # Create file at deep level
        (deep_path / "deep.md").write_text("deep content")

        # Create file at shallow level
        (base_path / "shallow.md").write_text("shallow content")

        from mcp_server_guide.tools.category_tools import _safe_glob_search

        results = _safe_glob_search(base_path, ["**/*.md"])

        # Should find shallow file but not deep file
        result_names = [f.name for f in results]
        assert "shallow.md" in result_names
        assert "deep.md" not in result_names
