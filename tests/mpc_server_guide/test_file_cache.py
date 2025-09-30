"""Tests for HTTP-aware file caching system (Issue 003 Phase 3)."""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
from mcp_server_guide.file_cache import FileCache, CacheEntry


def test_cache_entry_with_http_headers():
    """Test creating cache entries with HTTP headers."""
    headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT", "etag": '"33a64df551425fcc55e4d42a148795d9f25f89d4"'}
    entry = CacheEntry("test content", headers=headers)
    assert entry.content == "test content"
    assert entry.last_modified == "Wed, 21 Oct 2015 07:28:00 GMT"
    assert entry.etag == '"33a64df551425fcc55e4d42a148795d9f25f89d4"'


def test_cache_entry_needs_validation():
    """Test cache entry validation logic."""
    # Entry with no cache headers needs validation
    entry1 = CacheEntry("content")
    assert entry1.needs_validation()

    # Entry with Last-Modified needs validation after some time
    headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT"}
    entry2 = CacheEntry("content", headers=headers)
    # Fresh entry doesn't need validation immediately
    assert not entry2.needs_validation()

    # Entry with Cache-Control max-age
    headers = {"cache-control": "max-age=3600"}
    entry3 = CacheEntry("content", headers=headers)
    assert not entry3.needs_validation()


def test_http_client_conditional_requests():
    """Test HTTP client making conditional requests."""
    from mcp_server_guide.http_client import HttpClient

    with patch("requests.get") as mock_get:
        # Mock 304 Not Modified response
        mock_response = Mock()
        mock_response.status_code = 304
        mock_response.headers = {}
        mock_get.return_value = mock_response

        client = HttpClient()

        # Make conditional request with If-Modified-Since
        result = client.get_conditional(
            "https://example.com/guide.md", if_modified_since="Wed, 21 Oct 2015 07:28:00 GMT"
        )

        # Should return None for 304 Not Modified
        assert result is None

        # Should have sent conditional headers
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert "If-Modified-Since" in headers


def test_http_client_conditional_with_etag():
    """Test HTTP client conditional requests with ETag."""
    from mcp_server_guide.http_client import HttpClient

    with patch("requests.get") as mock_get:
        # Mock 304 Not Modified response
        mock_response = Mock()
        mock_response.status_code = 304
        mock_get.return_value = mock_response

        client = HttpClient()

        # Make conditional request with If-None-Match
        result = client.get_conditional(
            "https://example.com/guide.md", if_none_match='"33a64df551425fcc55e4d42a148795d9f25f89d4"'
        )

        assert result is None

        # Should have sent ETag header
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert "If-None-Match" in headers


def test_http_client_conditional_modified():
    """Test HTTP client when resource is modified."""
    from mcp_server_guide.http_client import HttpClient

    with patch("requests.get") as mock_get:
        # Mock 200 OK response with new content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Updated content"
        mock_response.headers = {"last-modified": "Thu, 22 Oct 2015 08:30:00 GMT", "etag": '"new-etag-value"'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = HttpClient()

        result = client.get_conditional(
            "https://example.com/guide.md", if_modified_since="Wed, 21 Oct 2015 07:28:00 GMT"
        )

        # Should return new content and headers
        assert result.content == "Updated content"
        assert result.headers["last-modified"] == "Thu, 22 Oct 2015 08:30:00 GMT"
        assert result.headers["etag"] == '"new-etag-value"'


def test_file_cache_with_validation():
    """Test file cache with HTTP validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = FileCache(cache_dir=temp_dir)

        # Put content with HTTP headers
        headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT", "etag": '"original-etag"'}
        cache.put("https://example.com/guide.md", "Original content", headers=headers)

        # Get should return content and validation info
        result = cache.get("https://example.com/guide.md")
        assert result.content == "Original content"
        assert result.last_modified == "Wed, 21 Oct 2015 07:28:00 GMT"
        assert result.etag == '"original-etag"'


def test_file_accessor_with_http_caching():
    """Test FileAccessor using HTTP-aware caching."""
    from mcp_server_guide.file_source import FileSource, FileAccessor

    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("mcp_server_guide.http_client.HttpClient") as mock_client_class:
            mock_client = Mock()

            # First request returns content with headers
            first_response = Mock()
            first_response.content = "# Guide v1"
            first_response.headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT", "etag": '"v1-etag"'}
            mock_client.get.return_value = first_response
            mock_client.get_conditional.return_value = None  # 304 Not Modified
            mock_client_class.return_value = mock_client

            http_source = FileSource("http", "https://example.com/docs/")
            accessor = FileAccessor(cache_dir=temp_dir)

            # First read - should fetch from HTTP and cache
            content1 = accessor.read_file("guide.md", http_source)
            assert content1 == "# Guide v1"
            assert mock_client.get.call_count == 1

            # Force cache to need validation by mocking time
            with patch("time.time", return_value=time.time() + 400):  # 400 seconds later
                # Second read - should make conditional request, get 304, use cache
                content2 = accessor.read_file("guide.md", http_source)
                assert content2 == "# Guide v1"
                assert mock_client.get_conditional.call_count == 1

                # Should have sent conditional headers
                call_args = mock_client.get_conditional.call_args
                assert call_args[1]["if_modified_since"] == "Wed, 21 Oct 2015 07:28:00 GMT"
                assert call_args[1]["if_none_match"] == '"v1-etag"'


def test_file_accessor_cache_invalidation():
    """Test cache invalidation when remote content changes."""
    from mcp_server_guide.file_source import FileSource, FileAccessor

    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("mcp_server_guide.http_client.HttpClient") as mock_client_class:
            mock_client = Mock()

            # First request
            first_response = Mock()
            first_response.content = "# Guide v1"
            first_response.headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT"}

            # Second request returns updated content
            updated_response = Mock()
            updated_response.content = "# Guide v2"
            updated_response.headers = {"last-modified": "Thu, 22 Oct 2015 08:30:00 GMT"}

            mock_client.get.return_value = first_response
            mock_client.get_conditional.return_value = updated_response  # Content changed
            mock_client_class.return_value = mock_client

            http_source = FileSource("http", "https://example.com/docs/")
            accessor = FileAccessor(cache_dir=temp_dir)

            # First read
            content1 = accessor.read_file("guide.md", http_source)
            assert content1 == "# Guide v1"

            # Force cache to need validation by mocking time
            with patch("time.time", return_value=time.time() + 400):  # 400 seconds later
                # Second read - content has changed
                content2 = accessor.read_file("guide.md", http_source)
                assert content2 == "# Guide v2"  # Should get updated content

                # Third read - should use updated cache
                content3 = accessor.read_file("guide.md", http_source)
                assert content3 == "# Guide v2"


def test_cache_respects_cache_control():
    """Test cache respecting Cache-Control headers."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = FileCache(cache_dir=temp_dir)

        # Content with no-cache directive
        headers = {"cache-control": "no-cache"}
        cache.put("https://example.com/no-cache.md", "No cache content", headers=headers)

        entry = cache.get("https://example.com/no-cache.md")
        assert entry.needs_validation()  # Should always need validation

        # Content with max-age
        headers = {"cache-control": "max-age=3600"}
        cache.put("https://example.com/cached.md", "Cached content", headers=headers)

        entry = cache.get("https://example.com/cached.md")
        assert not entry.needs_validation()  # Fresh for 1 hour


def test_fallback_to_cache_on_network_error():
    """Test falling back to cache when network fails."""
    from mcp_server_guide.file_source import FileSource, FileAccessor
    from mcp_server_guide.http_client import HttpError

    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("mcp_server_guide.http_client.HttpClient") as mock_client_class:
            mock_client = Mock()

            # First request succeeds
            first_response = Mock()
            first_response.content = "# Cached Guide"
            first_response.headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT"}
            mock_client.get.return_value = first_response

            # Second request fails
            mock_client.get_conditional.side_effect = HttpError("Network error")
            mock_client_class.return_value = mock_client

            http_source = FileSource("http", "https://example.com/docs/")
            accessor = FileAccessor(cache_dir=temp_dir)

            # First read - populates cache
            content1 = accessor.read_file("guide.md", http_source)
            assert content1 == "# Cached Guide"

            # Second read - network fails, should fall back to cache
            content2 = accessor.read_file("guide.md", http_source)
            assert content2 == "# Cached Guide"  # Should get cached content


def test_file_cache_edge_cases():
    """Test file cache edge cases to hit all branches."""
    cache = FileCache()

    # Test cache miss with non-existent URL
    result = cache.get("http://nonexistent.com/file.txt")
    assert result is None

    # Test cache put and get
    cache.put("http://example.com/test.txt", "test content", {"Last-Modified": "Wed, 21 Oct 2015 07:28:00 GMT"})
    result = cache.get("http://example.com/test.txt")
    assert result is not None
    assert result.content == "test content"

    # Test cache clear
    cache.clear()
    result = cache.get("http://example.com/test.txt")
    assert result is None


def test_file_cache_permission_error_fallback():
    """Test that FileCache falls back to temp directory on permission error."""
    from unittest.mock import patch
    import tempfile

    # Mock Path.mkdir to raise PermissionError on first call, succeed on second
    original_mkdir = Path.mkdir
    call_count = 0

    def mock_mkdir(self, parents=False, exist_ok=False):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise PermissionError("Permission denied")
        return original_mkdir(self, parents=parents, exist_ok=exist_ok)

    with patch.object(Path, "mkdir", mock_mkdir):
        cache = FileCache()
        # Should fallback to temp directory
        assert str(cache.cache_dir).startswith(tempfile.gettempdir())
        assert cache.cache_dir.name == "mcp-server-guide"
    """Test file cache comprehensive functionality."""
    cache = FileCache()

    # Test cache operations
    cache.put("http://test.com/file1.txt", "content1")
    entry = cache.get("http://test.com/file1.txt")
    assert entry is not None
    assert entry.content == "content1"

    # Test with headers - use lowercase keys as expected by the properties
    headers = {"etag": "123456", "cache-control": "max-age=3600"}
    cache.put("http://test.com/file2.txt", "content2", headers)
    entry = cache.get("http://test.com/file2.txt")
    assert entry is not None
    assert entry.etag == "123456"
    # Test cache entry validation
    assert not entry.needs_validation()  # Should not need validation with max-age
