"""Tests for session config validation using Pydantic."""

import pytest
from mcp_server_guide.session import SessionState


class TestSessionConfigKeyValidation:
    """Test that set_project_config validates keys against ProjectConfig fields."""

    def test_valid_key_categories_accepted(self):
        """Test that 'categories' key is accepted."""
        session = SessionState("test-project")

        # Should not raise
        session.set_project_config("categories", {"test": {"dir": "test/", "patterns": ["*.md"]}})

        # Verify the category was set correctly
        assert "test" in session.project_config.categories
        test_category = session.project_config.categories["test"]
        assert test_category.dir == "test/"
        assert test_category.patterns == ["*.md"]

    def test_invalid_key_rejected(self):
        """Test that invalid keys are rejected by Pydantic validation."""
        session = SessionState("test-project")

        with pytest.raises(ValueError) as exc_info:
            session.set_project_config("invalid_key", "some_value")

        error_msg = str(exc_info.value)
        assert "Invalid project configuration" in error_msg
        # Pydantic will mention extra fields not permitted
        assert "extra" in error_msg.lower() or "unexpected" in error_msg.lower()

    def test_dotted_key_rejected(self):
        """Test that dotted notation keys are rejected by Pydantic."""
        session = SessionState("test-project")

        with pytest.raises(ValueError) as exc_info:
            session.set_project_config("categories.test", "value")

        error_msg = str(exc_info.value)
        assert "Invalid project configuration" in error_msg

    def test_obsolete_docroot_key_rejected(self):
        """Test that obsolete 'docroot' key is rejected (it's now global, not per-project)."""
        session = SessionState("test-project")

        with pytest.raises(ValueError) as exc_info:
            session.set_project_config("docroot", "/some/path")

        assert "Invalid project configuration" in str(exc_info.value)

    def test_obsolete_guide_key_rejected(self):
        """Test that obsolete 'guide' key is rejected."""
        session = SessionState("test-project")

        with pytest.raises(ValueError) as exc_info:
            session.set_project_config("guide", "https://example.com/guide.md")

        assert "Invalid project configuration" in str(exc_info.value)

    def test_obsolete_language_key_rejected(self):
        """Test that obsolete 'language' key is rejected."""
        session = SessionState("test-project")

        with pytest.raises(ValueError) as exc_info:
            session.set_project_config("language", "python")

        assert "Invalid project configuration" in str(exc_info.value)

    def test_obsolete_guidelines_key_rejected(self):
        """Test that obsolete 'guidelines' key is rejected."""
        session = SessionState("test-project")

        with pytest.raises(ValueError) as exc_info:
            session.set_project_config("guidelines", "python-web")

        assert "Invalid project configuration" in str(exc_info.value)

    def test_empty_key_rejected(self):
        """Test that empty key is rejected."""
        session = SessionState("test-project")

        with pytest.raises(ValueError) as exc_info:
            session.set_project_config("", "value")

        assert "Invalid project configuration" in str(exc_info.value)

    def test_pydantic_validates_category_structure(self):
        """Test that Pydantic validates the category structure, not just keys."""
        session = SessionState("test-project")

        # Invalid category structure (missing required 'dir' field)
        with pytest.raises(ValueError) as exc_info:
            session.set_project_config("categories", {"test": {"patterns": ["*.md"]}})

        error_msg = str(exc_info.value)
        assert "Invalid project configuration" in error_msg
        # Pydantic should mention the missing field
        assert "dir" in error_msg.lower() or "field required" in error_msg.lower()

    def test_multiple_valid_operations(self):
        """Test multiple valid set operations work correctly."""
        session = SessionState("test-project")

        # Set categories multiple times
        session.set_project_config("categories", {"test1": {"dir": "test1/", "patterns": ["*.md"]}})
        assert "test1" in session.project_config.categories

        session.set_project_config("categories", {"test2": {"dir": "test2/", "patterns": ["*.py"]}})
        # After second set, should only have test2
        assert "test2" in session.project_config.categories
        assert "test1" not in session.project_config.categories
        test2_category = session.project_config.categories["test2"]
        assert test2_category.dir == "test2/"
        assert test2_category.patterns == ["*.py"]
