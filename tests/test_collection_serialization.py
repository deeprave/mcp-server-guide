"""Tests for collection serialization via model_dump()."""

from mcp_server_guide.project_config import ProjectConfig
from mcp_server_guide.models.collection import Collection
from mcp_server_guide.models.category import Category
from datetime import datetime, timezone


class TestCollectionSerialization:
    """Test that collections serialize properly via model_dump()."""

    def test_collections_serialize_properly_via_model_dump(self):
        """Test that collections serialize correctly without explicit handling."""
        # Create config with collections
        collection = Collection(
            categories=["guide", "lang"],
            description="Test collection",
            source_type="user",
            created_date=datetime.now(timezone.utc),
            modified_date=datetime.now(timezone.utc),
        )

        project_config = ProjectConfig(
            categories={
                "guide": Category(dir="guide/", patterns=["*.md"], description="Guide category"),
                "lang": Category(dir="lang/", patterns=["*.py"], description="Language category"),
            },
            collections={"test_collection": collection},
        )

        # Verify model_dump() includes collections properly
        dumped = project_config.model_dump(exclude_none=True)

        # Collections should be present and properly serialized
        assert "collections" in dumped
        assert "test_collection" in dumped["collections"]

        # Collection should be a dict (serialized), not a Collection object
        collection_data = dumped["collections"]["test_collection"]
        assert isinstance(collection_data, dict)
        assert not isinstance(collection_data, Collection)

        # Verify collection fields are properly serialized
        assert collection_data["categories"] == ["guide", "lang"]
        assert collection_data["description"] == "Test collection"
        assert collection_data["source_type"] == "user"
        assert "created_date" in collection_data
        assert "modified_date" in collection_data
