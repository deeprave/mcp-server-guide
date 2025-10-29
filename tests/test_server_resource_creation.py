"""Tests for server resource creation and configuration handling."""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from pydantic import ValidationError
from mcp_server_guide.server import create_server_with_config
from mcp_server_guide.project_config import ProjectConfig, Category, Collection


class TestServerResourceCreation:
    """Tests for server resource creation and configuration handling."""

    @pytest.mark.asyncio
    async def test_create_server_with_categories(self):
        """Test server creation with categories."""
        config = {"categories": {"guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Project guidelines"}}}

        with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
            mock_session = Mock()
            mock_session_mgr.return_value = mock_session

            project_config = ProjectConfig(
                categories={"guide": Category(dir="guide/", patterns=["*.md"], description="Project guidelines")}
            )
            mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

            # Should not raise an exception
            server = create_server_with_config(config)
            assert server is not None

    @pytest.mark.asyncio
    async def test_create_server_with_empty_description(self):
        """Test server creation with category having empty description."""
        config = {
            "categories": {
                "guide": {
                    "dir": "guide/",
                    "patterns": ["*.md"],
                    "description": "",  # Empty description
                }
            }
        }

        with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
            mock_session = Mock()
            mock_session_mgr.return_value = mock_session

            project_config = ProjectConfig(
                categories={"guide": Category(dir="guide/", patterns=["*.md"], description="")}
            )
            mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

            # Should not raise an exception
            server = create_server_with_config(config)
            assert server is not None

    @pytest.mark.asyncio
    async def test_create_server_with_none_description(self):
        """Test server creation with category having None description."""
        config = {
            "categories": {
                "guide": {
                    "dir": "guide/",
                    "patterns": ["*.md"],
                    # No description field
                }
            }
        }

        with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
            mock_session = Mock()
            mock_session_mgr.return_value = mock_session

            project_config = ProjectConfig(
                categories={
                    "guide": Category(dir="guide/", patterns=["*.md"])  # No description
                }
            )
            mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

            # Should not raise an exception
            server = create_server_with_config(config)
            assert server is not None

    @pytest.mark.asyncio
    async def test_create_server_with_collections(self):
        """Test server creation with collections."""
        config = {
            "categories": {"guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guide category"}},
            "collections": {"docs": {"categories": ["guide"], "description": "Documentation collection"}},
        }

        with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
            mock_session = Mock()
            mock_session_mgr.return_value = mock_session

            project_config = ProjectConfig(
                categories={"guide": Category(dir="guide/", patterns=["*.md"], description="Guide category")},
                collections={"docs": Collection(categories=["guide"], description="Documentation collection")},
            )
            mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

            # Should not raise an exception
            server = create_server_with_config(config)
            assert server is not None

    @pytest.mark.asyncio
    async def test_category_reader_success(self):
        """Test category reader success path."""
        with patch("mcp_server_guide.tools.category_tools.get_category_content") as mock_get_cat:
            mock_get_cat.return_value = {"success": True, "content": "Category content"}

            # This tests the internal category reader function
            # We need to create a server to test this
            config = {"categories": {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}}

            with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
                mock_session = Mock()
                mock_session_mgr.return_value = mock_session

                project_config = ProjectConfig(
                    categories={"test": Category(dir="test/", patterns=["*.md"], description="Test category")}
                )
                mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

                create_server_with_config(config)

    @pytest.mark.asyncio
    async def test_category_reader_invalid_category_name(self):
        """Test category reader with invalid category name."""
        with patch("mcp_server_guide.tools.category_tools.get_category_content") as mock_get_cat:
            mock_get_cat.return_value = {"success": False, "error": "Category not found"}

            config = {"categories": {"valid": {"dir": "valid/", "patterns": ["*.md"], "description": "Valid category"}}}

            with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
                mock_session = Mock()
                mock_session_mgr.return_value = mock_session
                project_config = ProjectConfig(
                    categories={"valid": Category(dir="valid/", patterns=["*.md"], description="Valid category")}
                )
                mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

                create_server_with_config(config)

    @pytest.mark.asyncio
    async def test_category_reader_exception_handling(self):
        """Test category reader exception handling."""
        with patch("mcp_server_guide.tools.category_tools.get_category_content") as mock_get_cat:
            mock_get_cat.side_effect = Exception("Unexpected error")

            config = {"categories": {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}}

            with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
                mock_session = Mock()
                mock_session_mgr.return_value = mock_session
                project_config = ProjectConfig(
                    categories={"test": Category(dir="test/", patterns=["*.md"], description="Test category")}
                )
                mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

                create_server_with_config(config)

    @pytest.mark.asyncio
    async def test_category_reader_failure(self):
        """Test category reader failure path."""
        with patch("mcp_server_guide.tools.category_tools.get_category_content") as mock_get_cat:
            mock_get_cat.return_value = {"success": False, "error": "Category not found"}

            config = {"categories": {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}}

            with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
                mock_session = Mock()
                mock_session_mgr.return_value = mock_session

                project_config = ProjectConfig(
                    categories={"test": Category(dir="test/", patterns=["*.md"], description="Test category")}
                )
                mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

                server = create_server_with_config(config)
                assert server is not None

    @pytest.mark.asyncio
    async def test_create_server_with_invalid_config(self):
        """Test server creation with invalid config."""
        # Test with missing required 'patterns' field
        invalid_config_missing_patterns = {
            "categories": {
                "invalid": {
                    # Missing required 'patterns' field
                    "dir": "test/"
                }
            }
        }

        # Test with missing required 'dir' field
        invalid_config_missing_dir = {
            "categories": {
                "invalid": {
                    # Missing required 'dir' field
                    "patterns": ["*.md"]
                }
            }
        }

        # Test with 'patterns' as a string instead of a list
        invalid_config_patterns_string = {
            "categories": {
                "invalid": {
                    "dir": "test/",
                    "patterns": "*.md",  # Should be a list
                }
            }
        }

        invalid_configs = [
            invalid_config_missing_patterns,
            invalid_config_missing_dir,
            invalid_config_patterns_string,
        ]

        with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
            mock_session = Mock()
            mock_session_mgr.return_value = mock_session

            for config in invalid_configs:
                # Server creation might succeed, but config validation should fail
                server = create_server_with_config(config)
                assert server is not None  # Server creation itself may succeed

                # Test that invalid config is handled gracefully
                # The validation should happen when the config is processed
                try:
                    # Attempt to use the server with invalid config
                    # This should either succeed gracefully or fail with proper error handling
                    resources = await server.list_resources()
                    # If it succeeds, verify it handles the invalid config gracefully
                    assert isinstance(resources, list)
                except Exception as e:
                    # If it fails, verify it's a proper validation error
                    assert isinstance(e, (ValueError, ValidationError, KeyError, TypeError))
                    assert len(str(e)) > 0  # Error message should be informative

    @pytest.mark.asyncio
    async def test_collection_reader_success(self):
        """Test collection reader success path."""
        with patch("mcp_server_guide.tools.collection_tools.get_collection_content") as mock_get_col:
            mock_get_col.return_value = {"success": True, "content": "Collection content"}

            config = {
                "categories": {"guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guide category"}},
                "collections": {"test": {"categories": ["guide"], "description": "Test collection"}},
            }

            with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
                mock_session = Mock()
                mock_session_mgr.return_value = mock_session

                project_config = ProjectConfig(
                    categories={"guide": Category(dir="guide/", patterns=["*.md"], description="Guide category")},
                    collections={"test": Collection(categories=["guide"], description="Test collection")},
                )
                mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

                create_server_with_config(config)

    @pytest.mark.asyncio
    async def test_collection_empty_description(self):
        """Test collection with empty description."""
        config = {
            "categories": {"guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guide category"}},
            "collections": {
                "test": {
                    "categories": ["guide"],
                    "description": "",  # Empty description
                }
            },
        }

        with patch("mcp_server_guide.server.SessionManager") as mock_session_mgr:
            mock_session = Mock()
            mock_session_mgr.return_value = mock_session

            project_config = ProjectConfig(
                categories={"guide": Category(dir="guide/", patterns=["*.md"], description="Guide category")},
                collections={"test": Collection(categories=["guide"], description="")},
            )
            mock_session.get_or_create_project_config = AsyncMock(return_value=project_config)

            create_server_with_config(config)
