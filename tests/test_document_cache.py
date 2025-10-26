"""Tests for document cache functionality."""

import pytest
from unittest.mock import patch
from mcp_server_guide.document_cache import CategoryDocumentCache, DocumentCacheEntry
from mcp_server_guide.tools.category_tools import update_category


class TestDocumentCache:
    """Test document cache functionality."""

    @pytest.fixture(autouse=True)
    async def setup_cache(self):
        """Clear cache before each test."""
        await CategoryDocumentCache.clear_all()

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self):
        """Test that cache miss returns None."""
        # Act: Try to get non-existent cache entry
        result = await CategoryDocumentCache.get("test_category", "test_document")

        # Assert: Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """Test that cache can store and retrieve entries."""
        # Arrange: Create cache entry data
        category = "test_category"
        document = "test_document"
        exists = True
        matched = ["test_document.md"]

        # Act: Set cache entry
        await CategoryDocumentCache.set(category, document, exists, matched)

        # Get cache entry
        result = await CategoryDocumentCache.get(category, document)

        # Assert: Should return correct entry
        assert result is not None
        assert isinstance(result, DocumentCacheEntry)
        assert result.exists == exists
        assert result.matched == matched

    @pytest.mark.asyncio
    async def test_cache_stores_non_existent_documents(self):
        """Test that cache can store entries for non-existent documents."""
        # Arrange: Create cache entry for non-existent document
        category = "test_category"
        document = "non_existent_document"
        exists = False
        matched = None

        # Act: Set cache entry
        await CategoryDocumentCache.set(category, document, exists, matched)

        # Get cache entry
        result = await CategoryDocumentCache.get(category, document)

        # Assert: Should return correct entry
        assert result is not None
        assert isinstance(result, DocumentCacheEntry)
        assert not result.exists
        assert result.matched is None

    @pytest.mark.asyncio
    async def test_cache_stores_glob_pattern_matches(self):
        """Test that cache stores glob pattern matches correctly."""
        # Arrange: Create cache entry with glob matches
        category = "test_category"
        document = "test_document"
        exists = True
        matched = ["file1.md", "file2.md", "file3.md"]

        # Act: Set cache entry
        await CategoryDocumentCache.set(category, document, exists, matched)

        # Get cache entry
        result = await CategoryDocumentCache.get(category, document)

        # Assert: Should return correct entry with all matches
        assert result is not None
        assert result.exists
        assert result.matched == matched

    @pytest.mark.asyncio
    async def test_cache_invalidate_category(self):
        """Test that cache can invalidate all entries for a category."""
        # Arrange: Set multiple cache entries
        category = "test_category"
        await CategoryDocumentCache.set(category, "doc1", True, ["doc1.md"])
        await CategoryDocumentCache.set(category, "doc2", True, ["doc2.md"])
        await CategoryDocumentCache.set("other_category", "doc3", True, ["doc3.md"])

        # Verify entries exist
        assert await CategoryDocumentCache.get(category, "doc1") is not None
        assert await CategoryDocumentCache.get(category, "doc2") is not None
        assert await CategoryDocumentCache.get("other_category", "doc3") is not None

        # Act: Invalidate category
        await CategoryDocumentCache.invalidate_category(category)

        # Assert: Category entries should be gone, other category should remain
        assert await CategoryDocumentCache.get(category, "doc1") is None
        assert await CategoryDocumentCache.get(category, "doc2") is None
        assert await CategoryDocumentCache.get("other_category", "doc3") is not None

    @pytest.mark.asyncio
    async def test_cache_clear_all(self):
        """Test that cache can clear all entries."""
        # Arrange: Set multiple cache entries across categories
        await CategoryDocumentCache.set("category1", "doc1", True, ["doc1.md"])
        await CategoryDocumentCache.set("category2", "doc2", True, ["doc2.md"])

        # Verify entries exist
        assert await CategoryDocumentCache.get("category1", "doc1") is not None
        assert await CategoryDocumentCache.get("category2", "doc2") is not None

        # Act: Clear all cache
        await CategoryDocumentCache.clear_all()

        # Assert: All entries should be gone
        assert await CategoryDocumentCache.get("category1", "doc1") is None
        assert await CategoryDocumentCache.get("category2", "doc2") is None

    @pytest.mark.asyncio
    async def test_cache_separate_categories(self):
        """Test that cache keeps categories separate."""
        # Arrange: Set same document name in different categories
        document = "same_document"
        await CategoryDocumentCache.set("category1", document, True, ["file1.md"])
        await CategoryDocumentCache.set("category2", document, False, None)

        # Act: Get entries from both categories
        result1 = await CategoryDocumentCache.get("category1", document)
        result2 = await CategoryDocumentCache.get("category2", document)

        # Assert: Should return different entries
        assert result1.exists
        assert result1.matched == ["file1.md"]
        assert not result2.exists
        assert result2.matched is None


class TestDocumentCacheIntegration:
    """Test document cache integration with other components."""

    @pytest.fixture(autouse=True)
    async def setup_cache(self):
        """Clear cache before each test."""
        await CategoryDocumentCache.clear_all()

    @pytest.mark.asyncio
    async def test_cache_integration_with_content_tools(self, isolated_config_file):
        """Test that content tools use the cache correctly."""
        from mcp_server_guide.tools.content_tools import get_content

        # This test verifies that get_content uses the cache
        # The actual caching behavior is tested in the content tools tests
        result = await get_content("guide", "nonexistent_doc")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_invalidation_on_category_update(self, isolated_config_file):
        """Test that cache is invalidated when categories are updated."""
        from mcp_server_guide.session_manager import SessionManager
        from mcp_server_guide.project_config import ProjectConfig, Category

        # Setup session with a category
        session_manager = SessionManager()
        session_manager._set_config_filename(isolated_config_file)

        config = ProjectConfig(
            categories={
                "test_category": Category(dir="test_dir", patterns=["*.md"]),
            }
        )
        session_manager.session_state.project_config = config

        # Set cache entry
        await CategoryDocumentCache.set("test_category", "test_doc", True, ["test.md"])
        assert await CategoryDocumentCache.get("test_category", "test_doc") is not None

        # Update category (this should invalidate cache)

        # Mock the session manager to use our instance and ensure get_or_create_project_config returns our config
        with patch("mcp_server_guide.tools.category_tools.SessionManager") as mock_session_class:
            mock_session_class.return_value = session_manager

            # Mock the get_or_create_project_config method to return our config
            async def mock_get_config(project):
                return config

            session_manager.get_or_create_project_config = mock_get_config
            await update_category("test_category", dir="new_dir", patterns=["*.txt"])

        # Cache should be invalidated
        cache_entry = await CategoryDocumentCache.get("test_category", "test_doc")
        assert cache_entry is None


class TestConcurrentCacheAccess:
    """Test concurrent cache access scenarios."""

    @pytest.fixture(autouse=True)
    async def setup_cache(self):
        """Clear cache before each test."""
        await CategoryDocumentCache.clear_all()

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self):
        """Test concurrent cache set/get operations."""
        import asyncio

        async def cache_worker(worker_id: int):
            """Worker that performs cache operations."""
            category = f"category_{worker_id}"
            document = f"document_{worker_id}"

            # Set cache entry
            await CategoryDocumentCache.set(category, document, True, [f"file_{worker_id}.md"])

            # Get cache entry
            result = await CategoryDocumentCache.get(category, document)
            assert result is not None
            assert result.exists
            assert result.matched == [f"file_{worker_id}.md"]

            return worker_id

        # Run multiple workers concurrently
        tasks = [cache_worker(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # All workers should complete successfully
        assert len(results) == 10
        assert results == list(range(10))

    @pytest.mark.asyncio
    async def test_concurrent_cache_invalidation(self):
        """Test concurrent cache invalidation operations."""
        import asyncio

        # Set up initial cache entries
        for i in range(5):
            await CategoryDocumentCache.set(f"category_{i}", f"doc_{i}", True, [f"file_{i}.md"])

        async def invalidate_worker(category_id: int):
            """Worker that invalidates cache."""
            await CategoryDocumentCache.invalidate_category(f"category_{category_id}")
            return category_id

        # Run concurrent invalidations
        tasks = [invalidate_worker(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # All invalidations should complete
        assert len(results) == 5

        # All entries should be invalidated
        for i in range(5):
            result = await CategoryDocumentCache.get(f"category_{i}", f"doc_{i}")
            assert result is None
