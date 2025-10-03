"""Tests for builtin category partial updates (Issue 030)."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.mcp_server_guide.tools.category_tools import update_category


@pytest.fixture
def mock_session():
    """Mock session manager with builtin categories."""
    with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock:
        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_current_project_safe.return_value = "test-project"
        session_instance.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {
                    "dir": "guide/",
                    "patterns": ["guidelines.md"],
                    "description": "Project guidelines",
                    "auto_load": False,
                },
                "lang": {
                    "dir": "lang/",
                    "patterns": ["python.md"],
                    "description": "Language guides",
                    "auto_load": True,
                },
                "context": {
                    "dir": "context/",
                    "patterns": ["context.md"],
                    "description": "Context files",
                    "auto_load": False,
                },
            }
        }
        session_instance.save_to_file = AsyncMock()
        yield session_instance


@pytest.mark.asyncio
async def test_update_builtin_category_dir_field(mock_session):
    """Test updating dir field on builtin category should succeed."""
    result = await update_category(
        name="guide",
        dir="new-guide/",
        patterns=["guidelines.md"],
        description="Project guidelines",
    )

    # This should pass once we implement the feature
    assert result["success"] is True
    assert result["category"]["dir"] == "new-guide/"
    assert result["category"]["patterns"] == ["guidelines.md"]
    assert result["category"]["description"] == "Project guidelines"


@pytest.mark.asyncio
async def test_update_builtin_category_patterns_field(mock_session):
    """Test updating patterns field on builtin category should succeed."""
    result = await update_category(
        name="lang",
        dir="lang/",
        patterns=["*.py", "*.md"],
        description="Language guides",
    )

    # This should pass once we implement the feature
    assert result["success"] is True
    assert result["category"]["dir"] == "lang/"
    assert result["category"]["patterns"] == ["*.py", "*.md"]
    assert result["category"]["description"] == "Language guides"


@pytest.mark.asyncio
async def test_update_builtin_category_auto_load_field(mock_session):
    """Test updating auto_load field on builtin category should succeed."""
    result = await update_category(
        name="context",
        dir="context/",
        patterns=["context.md"],
        description="Context files",
        auto_load=True,
    )

    # This should pass once we implement the feature
    assert result["success"] is True
    assert result["category"]["dir"] == "context/"
    assert result["category"]["patterns"] == ["context.md"]
    assert result["category"]["description"] == "Context files"
    assert result["category"]["auto_load"] is True


@pytest.mark.asyncio
async def test_builtin_category_deletion_still_forbidden(mock_session):
    """Test that deleting builtin categories is still forbidden."""
    from src.mcp_server_guide.tools.category_tools import remove_category

    result = await remove_category("guide")

    assert result["success"] is False
    assert "Cannot remove built-in category" in result["error"]


@pytest.mark.asyncio
async def test_update_builtin_category_invalid_field_rejected(mock_session):
    """Test that updating with invalid configuration is rejected."""
    # Test with invalid patterns (empty list should be rejected by validation)
    result = await update_category(
        name="guide",
        dir="guide/",
        patterns=[],  # Empty patterns should be invalid
        description="Project guidelines",
    )

    # This should fail due to validation
    assert result["success"] is False
    assert "Invalid category configuration" in result["error"]
