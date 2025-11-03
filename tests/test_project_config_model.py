"""Tests for ProjectConfig model validation and methods."""

import pytest
from pydantic import ValidationError
from mcp_server_guide.models.project_config import ProjectConfig
from mcp_server_guide.models.category import Category
from mcp_server_guide.models.collection import Collection


class TestProjectConfigValidation:
    """Test ProjectConfig validation methods."""

    def test_valid_category_names(self):
        """Test that valid category names are accepted."""
        valid_names = ["test", "test_category", "test-category", "category123", "a1b2c3"]

        for name in valid_names:
            config = ProjectConfig(categories={name: Category(dir="test/", patterns=["*.md"])})
            assert name in config.categories

    def test_invalid_category_names(self):
        """Test that invalid category names are rejected."""
        invalid_names = ["123test", "_test", "-test", "test space", "test@category", ""]

        for name in invalid_names:
            with pytest.raises(ValueError, match="must start with a letter"):
                ProjectConfig(categories={name: Category(dir="test/", patterns=["*.md"])})

    def test_category_name_length_limit(self):
        """Test that category names exceeding 30 characters are rejected."""
        long_name = "a" * 31  # 31 characters

        with pytest.raises(ValueError, match="cannot exceed 30 characters"):
            ProjectConfig(categories={long_name: Category(dir="test/", patterns=["*.md"])})

    def test_categories_dict_conversion(self):
        """Test that category dictionaries are converted to Category objects."""
        config = ProjectConfig(
            categories={"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test category"}}
        )

        assert isinstance(config.categories["test"], Category)
        assert config.categories["test"].dir == "test/"
        assert config.categories["test"].patterns == ["*.md"]
        assert config.categories["test"].description == "Test category"

    def test_categories_invalid_dict_data(self):
        """Test that invalid category dictionary data raises error."""
        with pytest.raises(ValidationError, match="Category must have either 'url' or 'dir' field"):
            ProjectConfig(
                categories={
                    "test": {"invalid": "data"}  # Missing required fields
                }
            )

    def test_categories_invalid_type(self):
        """Test that non-dict, non-Category values are rejected."""
        with pytest.raises(ValidationError, match="Input should be a valid dictionary or instance of Category"):
            ProjectConfig(categories={"test": "invalid_string"})

    def test_collections_validation(self):
        """Test collections validation."""
        config = ProjectConfig(
            categories={"guide": Category(dir="guide/", patterns=["*.md"])},
            collections={"test": Collection(categories=["guide"], description="Test collection")},
        )

        assert isinstance(config.collections["test"], Collection)
        assert config.collections["test"].categories == ["guide"]

    def test_collections_invalid_name(self):
        """Test that invalid collection names are rejected."""
        with pytest.raises(ValueError, match="Collection name.*is invalid"):
            ProjectConfig(collections={"123invalid": Collection(categories=["test"])})

    def test_collections_name_too_long(self):
        """Test that collection names exceeding 30 characters are rejected."""
        long_name = "a" * 31

        with pytest.raises(ValueError, match="is too long"):
            ProjectConfig(collections={long_name: Collection(categories=["test"])})

    def test_collections_dict_conversion(self):
        """Test that collection dictionaries are converted to Collection objects."""
        config = ProjectConfig(
            categories={"guide": Category(dir="guide/", patterns=["*.md"])},
            collections={"test": {"categories": ["guide"], "description": "Test"}},
        )

        assert isinstance(config.collections["test"], Collection)
        assert config.collections["test"].categories == ["guide"]

    def test_collections_invalid_type(self):
        """Test that invalid collection types are rejected."""
        with pytest.raises(ValidationError, match="Input should be a valid dictionary or instance of Collection"):
            ProjectConfig(collections={"test": "invalid_string"})

    def test_collections_not_dict(self):
        """Test that non-dict collections value is rejected."""
        with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
            ProjectConfig(collections="not_a_dict")


class TestProjectConfigMethods:
    """Test ProjectConfig methods."""

    def test_model_dump_includes_collections(self):
        """Test that model_dump always includes collections."""
        config = ProjectConfig(categories={"test": Category(dir="test/", patterns=["*.md"])})

        data = config.model_dump()

        assert "collections" in data
        assert data["collections"] == {}

    def test_to_dict_excludes_none_and_empty(self):
        """Test that to_dict excludes None values and empty lists."""
        config = ProjectConfig(categories={"test": Category(dir="test/", patterns=["*.md"])}, collections={})

        data = config.to_dict()

        assert "collections" in data  # Always included even if empty
        assert data["collections"] == {}

    def test_to_dict_includes_non_empty_values(self):
        """Test that to_dict includes non-empty values."""
        config = ProjectConfig(
            categories={"test": Category(dir="test/", patterns=["*.md"])},
            collections={"test": Collection(categories=["test"], description="Test")},
        )

        data = config.to_dict()

        assert "categories" in data
        assert "collections" in data
        assert len(data["collections"]) == 1

    def test_from_dict_creates_config(self):
        """Test that from_dict creates ProjectConfig from dictionary."""
        data = {
            "categories": {"test": {"dir": "test/", "patterns": ["*.md"], "description": "Test"}},
            "collections": {"test_collection": {"categories": ["test"], "description": "Test collection"}},
        }

        config = ProjectConfig.from_dict(data)

        assert isinstance(config, ProjectConfig)
        assert "test" in config.categories
        assert "test_collection" in config.collections

    def test_model_post_init_validates_collection_references(self):
        """Test that model_post_init validates collection category references."""
        # This should not raise an error but may log a warning
        config = ProjectConfig(
            categories={"existing": Category(dir="test/", patterns=["*.md"])},
            collections={"test": Collection(categories=["existing", "missing"])},
        )

        # Should create successfully despite missing category reference
        assert config is not None
        assert "test" in config.collections

    def test_empty_config_creation(self):
        """Test creating empty ProjectConfig."""
        config = ProjectConfig()

        assert config.categories == {}
        assert config.collections == {}

    def test_config_with_only_categories(self):
        """Test creating config with only categories."""
        config = ProjectConfig(categories={"test": Category(dir="test/", patterns=["*.md"])})

        assert len(config.categories) == 1
        assert config.collections == {}

    def test_config_with_only_collections(self):
        """Test creating config with only collections."""
        config = ProjectConfig(collections={"test": Collection(categories=["nonexistent"])})

        assert config.categories == {}
        assert len(config.collections) == 1


class TestProjectConfigEdgeCases:
    """Test ProjectConfig edge cases and error conditions."""

    def test_categories_none_value(self):
        """Test handling None value for categories."""
        with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
            ProjectConfig(categories=None)

    def test_collections_none_value(self):
        """Test handling None value for collections."""
        with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
            ProjectConfig(collections=None)

    def test_category_with_empty_patterns(self):
        """Test category with empty patterns list."""
        config = ProjectConfig(categories={"test": Category(dir="test/", patterns=[])})

        assert config.categories["test"].patterns == []

    def test_collection_with_empty_categories(self):
        """Test collection with empty categories list raises validation error."""
        with pytest.raises(ValidationError, match="Collection must contain at least one category"):
            ProjectConfig(collections={"test": Collection(categories=[])})

    def test_large_valid_data(self):
        """Test with large but valid data structures."""
        categories = {}
        collections = {}

        # Create 10 categories
        for i in range(10):
            name = f"category{i}"
            categories[name] = Category(dir=f"dir{i}/", patterns=[f"*.{i}"])

        # Create 5 collections
        for i in range(5):
            name = f"collection{i}"
            collections[name] = Collection(
                categories=[f"category{j}" for j in range(i, i + 3) if j < 10], description=f"Collection {i}"
            )

        config = ProjectConfig(categories=categories, collections=collections)

        assert len(config.categories) == 10
        assert len(config.collections) == 5
