"""Tests for category updates on former builtin categories (Phase 1)."""

from unittest.mock import Mock, patch

import pytest

from mcp_server_guide.tools.category_tools import remove_category, update_category


@pytest.fixture
def mock_session():
    """Mock session manager for testing."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock project config with guide category
        mock_config = Mock()
        mock_config.categories = {"guide": Mock()}
        mock_session.session_state.project_config = mock_config
        mock_session.get_project_name.return_value = "test_project"

        # Make get_or_create_project_config async
        async def async_get_config(project):
            return mock_config

        mock_session.get_or_create_project_config = async_get_config

        # Make save_project_config async
        async def async_save_config(config):
            return None

        mock_session.save_project_config = async_save_config

        # Make safe_save_session async
        async def async_safe_save():
            return None

        mock_session.safe_save_session = async_safe_save

        yield mock_session


@pytest.mark.asyncio
async def test_update_former_builtin_category_dir_field(mock_session):
    """Test updating dir field on former builtin category succeeds."""
    result = await update_category(
        name="guide",
        dir="new-guide/",
        patterns=["guidelines.md"],
        description="Project guidelines",
    )

    # This should succeed - no builtin protection
    assert result["success"] is True


@pytest.mark.asyncio
async def test_update_former_builtin_category_patterns_field(mock_session):
    """Test updating patterns field on former builtin category succeeds."""
    result = await update_category(
        name="guide",
        patterns=["*.guide", "guide-*.md"],
    )

    # This should succeed - no builtin protection
    assert result["success"] is True


@pytest.mark.asyncio
async def test_update_former_builtin_category_description_field(mock_session):
    """Test updating description field on former builtin category succeeds."""
    result = await update_category(
        name="guide",
        description="Updated project guidelines",
    )

    # This should succeed - no builtin protection
    assert result["success"] is True


@pytest.mark.asyncio
async def test_former_builtin_category_deletion_allowed(mock_session):
    """Test that deleting former builtin categories is now allowed."""
    result = await remove_category("guide")

    # This should succeed - no builtin protection
    assert result["success"] is True


@pytest.mark.asyncio
async def test_update_former_builtin_category_all_fields(mock_session):
    """Test that updating all fields on former builtin category succeeds."""
    result = await update_category(
        name="guide",
        dir="updated-guide/",
        patterns=["*.guide", "guide-*.md"],
        description="Updated project guidelines",
    )

    # This should succeed - no builtin protection
    assert result["success"] is True
