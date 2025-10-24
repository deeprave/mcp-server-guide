"""Test that category operations preserve all ProjectConfig fields."""

import pytest
from src.mcp_server_guide.tools.category_tools import remove_category
from src.mcp_server_guide.project_config import ProjectConfig, Category
from src.mcp_server_guide.session_manager import SessionManager


@pytest.fixture
def session_with_categories(isolated_config_file):
    """Create session with ProjectConfig containing multiple categories."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Create config with multiple categories
    config = ProjectConfig(
        categories={
            "test_category": Category(dir="test_dir", patterns=["*.md"], description="Test category", auto_load=True),
            "keep_category": Category(dir="keep_dir", patterns=["*.txt"], description="Keep this one", auto_load=False),
        }
    )

    session_manager.session_state.project_config = config
    return session_manager


@pytest.mark.asyncio
async def test_remove_category_preserves_other_categories_and_their_fields(session_with_categories):
    """Test that removing a category preserves other categories with all their fields."""
    session = session_with_categories
    original_config = session.session_state.project_config

    # Verify original config has both categories with all fields
    assert "test_category" in original_config.categories
    assert "keep_category" in original_config.categories
    assert original_config.categories["test_category"].description == "Test category"
    assert original_config.categories["test_category"].auto_load is True
    assert original_config.categories["keep_category"].description == "Keep this one"
    assert original_config.categories["keep_category"].auto_load is False

    # Remove one category
    await remove_category("test_category")

    # Verify the remaining category preserves all its fields
    updated_config = session.session_state.project_config
    assert "test_category" not in updated_config.categories  # Should be removed
    assert "keep_category" in updated_config.categories  # Should be preserved

    # Critical: All fields of remaining category should be preserved
    kept_category = updated_config.categories["keep_category"]
    assert kept_category.description == "Keep this one"  # Field preservation test
    assert kept_category.auto_load is False  # Field preservation test
    assert kept_category.dir == "keep_dir/"  # Field preservation test (normalized with trailing slash)
    assert kept_category.patterns == ["*.txt"]  # Field preservation test


class TestCategoryUpdatesAndEdgeCases:
    """Test category updates and edge cases like removing the last category."""

    @pytest.mark.asyncio
    async def test_remove_last_category(self, isolated_config_file):
        """Test removing the last category in the config."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Create config with single category
        config = ProjectConfig(
            categories={
                "only_category": Category(dir="only_dir", patterns=["*.md"], description="Only one", auto_load=True),
            }
        )
        session_manager.session_state.project_config = config

        # Remove the only category
        await remove_category("only_category")

        # Config should have empty categories dict
        updated_config = session_manager.session_state.project_config
        assert updated_config.categories == {}

    @pytest.mark.asyncio
    async def test_remove_nonexistent_category(self, isolated_config_file):
        """Test removing a category that doesn't exist."""
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        config = ProjectConfig(
            categories={
                "existing": Category(dir="test_dir", patterns=["*.md"]),
            }
        )
        session_manager.session_state.project_config = config

        # Try to remove non-existent category
        result = await remove_category("nonexistent")

        # Should handle gracefully with specific error message
        assert not result["success"]
        assert "does not exist" in result["error"]
        assert "nonexistent" in result["error"]  # Verify category name is in error message

        # Existing category should remain
        updated_config = session_manager.session_state.project_config
        assert "existing" in updated_config.categories

    @pytest.mark.asyncio
    async def test_category_update_preserves_fields(self, isolated_config_file):
        """Test that updating categories preserves all fields."""
        from src.mcp_server_guide.tools.category_tools import update_category

        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        # Create config with category having all fields
        config = ProjectConfig(
            categories={
                "update_me": Category(dir="old_dir", patterns=["*.old"], description="Old description", auto_load=True),
            }
        )
        session_manager.session_state.project_config = config

        # Save the session to ensure the config is persisted
        await session_manager.save_session()

        # Update category
        result = await update_category(
            "update_me", "new_dir", ["*.new"], description="New description", auto_load=False
        )

        # Ensure update succeeded
        assert result["success"], f"Update failed: {result.get('error', 'Unknown error')}"

        # All fields should be updated correctly
        updated_config = session_manager.session_state.project_config
        updated_category = updated_config.categories["update_me"]
        assert updated_category.dir == "new_dir/"
        assert updated_category.patterns == ["*.new"]
        assert updated_category.description == "New description"
        assert updated_category.auto_load is False
