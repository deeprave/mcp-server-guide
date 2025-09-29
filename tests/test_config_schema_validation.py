"""Tests for configuration schema validation."""

import pytest
from src.mcp_server_guide.validation import (
    validate_config,
    validate_config_key,
    validate_category,
    ConfigValidationError,
    is_valid_config_key,
)


class TestConfigSchemaValidation:
    """Test configuration schema validation functionality."""

    def test_validate_valid_config(self):
        """Test that valid configuration passes validation."""
        config = {
            "project": "test-project",
            "docroot": "/path/to/docs",
            "tools": ["tool1", "tool2"],
            "categories": {
                "guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guidelines", "auto_load": True}
            },
        }
        # Should not raise any exception
        validate_config(config)

    def test_validate_config_rejects_invalid_keys(self):
        """Test that configuration with invalid top-level keys is rejected."""
        config = {"project": "test-project", "invalid_key": "should_fail"}
        with pytest.raises(ConfigValidationError):
            validate_config(config)

    def test_validate_config_key_valid_keys(self):
        """Test that valid configuration keys are accepted."""
        validate_config_key("project", "test-project")
        validate_config_key("docroot", "/path/to/docs")
        validate_config_key("tools", ["tool1", "tool2"])
        validate_config_key(
            "categories", {"guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guidelines"}}
        )

    def test_validate_config_key_invalid_key(self):
        """Test that invalid configuration keys are rejected."""
        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config_key("categories.scm.auto_load", True)

        assert "Invalid configuration key" in str(exc_info.value)
        assert "categories.scm.auto_load" in str(exc_info.value)

    def test_validate_config_key_invalid_value_type(self):
        """Test that invalid value types are rejected."""
        with pytest.raises(ConfigValidationError):
            validate_config_key("project", 123)  # Should be string

        with pytest.raises(ConfigValidationError):
            validate_config_key("tools", "not_an_array")  # Should be array

    def test_validate_category_valid(self):
        """Test that valid category definitions are accepted."""
        category_data = {"dir": "guide/", "patterns": ["*.md"], "description": "Guidelines", "auto_load": True}
        validate_category("guide", category_data)

    def test_validate_category_invalid_name(self):
        """Test that invalid category names are rejected."""
        category_data = {"dir": "guide/", "patterns": ["*.md"], "description": "Guidelines"}

        # Names starting with numbers
        with pytest.raises(ConfigValidationError):
            validate_category("123invalid", category_data)

        # Names with invalid characters
        with pytest.raises(ConfigValidationError):
            validate_category("invalid@name", category_data)

    def test_validate_category_missing_required_fields(self):
        """Test that categories missing required fields are rejected."""
        # Missing 'dir'
        with pytest.raises(ConfigValidationError):
            validate_category("guide", {"patterns": ["*.md"], "description": "Guidelines"})

        # Missing 'patterns'
        with pytest.raises(ConfigValidationError):
            validate_category("guide", {"dir": "guide/", "description": "Guidelines"})

        # Missing 'description'
        with pytest.raises(ConfigValidationError):
            validate_category("guide", {"dir": "guide/", "patterns": ["*.md"]})

    def test_validate_category_invalid_patterns(self):
        """Test that invalid patterns are rejected."""
        with pytest.raises(ConfigValidationError):
            validate_category(
                "guide",
                {
                    "dir": "guide/",
                    "patterns": [],  # Empty array not allowed
                    "description": "Guidelines",
                },
            )

    def test_is_valid_config_key(self):
        """Test the is_valid_config_key utility function."""
        assert is_valid_config_key("project") is True
        assert is_valid_config_key("docroot") is True
        assert is_valid_config_key("tools") is True
        assert is_valid_config_key("categories") is True

        assert is_valid_config_key("invalid_key") is False
        assert is_valid_config_key("categories.scm.auto_load") is False

    def test_config_validation_error_with_multiple_errors(self):
        """Test that ConfigValidationError can contain multiple error messages."""
        config = {
            "project": 123,  # Should be string
            "tools": "not_array",  # Should be array
            "invalid_key": "value",  # Invalid key
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config(config)

        error = exc_info.value
        assert len(error.errors) > 0
        assert isinstance(error.errors, list)


class TestConfigSchemaIntegration:
    """Test integration scenarios for configuration schema validation."""

    def test_real_world_config_structure(self):
        """Test validation with a realistic configuration structure."""
        config = {
            "project": "mcp-server-guide",
            "docroot": "/Users/user/Code/project",
            "tools": ["example-tool", "another-tool"],
            "categories": {
                "guide": {
                    "dir": "aidocs/guide/",
                    "patterns": ["**/*.md"],
                    "description": "Development methodology, TDD approach, and SOLID/YAGNI guardrails",
                    "auto_load": True,
                },
                "lang": {
                    "dir": "aidocs/lang/",
                    "patterns": ["python.md"],
                    "description": "Language-specific coding standards",
                    "auto_load": True,
                },
                "context": {
                    "dir": "aidocs/context/",
                    "patterns": ["freeform.md"],
                    "description": "Project-specific information",
                    "auto_load": True,
                },
                "scm": {
                    "dir": "aidocs/scm",
                    "patterns": ["**/*.md"],
                    "description": "Source Code Management guidelines",
                    "auto_load": True,
                },
            },
        }

        # Should validate successfully
        validate_config(config)

    def test_prevents_dotted_key_pollution(self):
        """Test that the schema prevents the original issue with dotted keys."""
        # This was the problematic key that caused the issue
        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config_key("categories.scm.auto_load", True)

        assert "Invalid configuration key 'categories.scm.auto_load'" in str(exc_info.value)
        assert "Dotted keys are not allowed" in str(exc_info.value)
