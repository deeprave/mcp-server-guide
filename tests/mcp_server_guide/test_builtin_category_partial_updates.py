"""Tests for builtin category partial updates (Issue 030)."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp_server_guide.tools.category_tools import update_category


@pytest.fixture
def mock_session():
    """Mock session manager with builtin categories."""
    with patch("mcp_server_guide.tools.category_tools.SessionManager") as mock:
        from mcp_server_guide.project_config import ProjectConfig, Category

        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_project_name = Mock(return_value="test-project")

        config_data = ProjectConfig(
            categories={
                "guide": Category(
                    dir="guide/",
                    patterns=["guidelines.md"],
                    description="Project guidelines",
                    auto_load=False,
                ),
                "lang": Category(
                    dir="lang/",
                    patterns=["python.md"],
                    description="Language guides",
                    auto_load=True,
                ),
                "context": Category(
                    dir="context/",
                    patterns=["context.md"],
                    description="Context files",
                    auto_load=False,
                ),
            }
        )

        session_instance.get_or_create_project_config = AsyncMock(return_value=config_data)
        session_instance.save_session = AsyncMock()
        yield session_instance


@pytest.mark.asyncio
async def test_update_builtin_category_dir_field(mock_session):
    """Test updating dir field on builtin category should fail (builtin protection)."""
    result = await update_category(
        name="guide",
        dir="new-guide/",
        patterns=["guidelines.md"],
        description="Project guidelines",
    )

    # This should fail because builtin categories are protected
    assert result["success"] is False
    assert "Cannot modify built-in category" in result["error"]


@pytest.mark.asyncio
async def test_update_builtin_category_patterns_field(mock_session):
    """Test updating patterns field on builtin category should fail (builtin protection)."""
    result = await update_category(
        name="lang",
        dir="lang/",
        patterns=["*.py", "*.md"],
        description="Language guides",
    )

    # This should fail because builtin categories are protected
    assert result["success"] is False
    assert "Cannot modify built-in category" in result["error"]


@pytest.mark.asyncio
async def test_update_builtin_category_description_field(mock_session):
    """Test updating description field on builtin category should fail (builtin protection)."""
    result = await update_category(
        name="context",
        description="Context files",
    )

    # This should fail because builtin categories are protected
    assert result["success"] is False
    assert "Cannot modify built-in category" in result["error"]


@pytest.mark.asyncio
async def test_builtin_category_deletion_still_forbidden(mock_session):
    """Test that deleting builtin categories is still forbidden."""
    from mcp_server_guide.tools.category_tools import remove_category

    result = await remove_category("guide")

    assert result["success"] is False
    assert "Cannot remove built-in category" in result["error"]


@pytest.mark.asyncio
async def test_update_builtin_category_invalid_field_rejected(mock_session):
    """Test that updating builtin category is rejected."""
    result = await update_category(
        name="guide",
        description="Project guidelines",
    )

    # This should fail because builtin categories are protected
    assert result["success"] is False
    assert "Cannot modify built-in category" in result["error"]
