"""Tests for FileSource functionality."""

import pytest
from mcp_server_guide.file_source import FileSource, FileAccessor, FileSourceType


def test_file_source_creation():
    """Test FileSource creation with different types."""
    # Local file source
    local_source = FileSource(FileSourceType.FILE, "/client/path")
    assert local_source.type == FileSourceType.FILE
    assert local_source.base_path == "/client/path"
    assert local_source.cache_enabled is True
    assert local_source.cache_ttl == 3600

    # Local file source (replaces SERVER)
    local_source = FileSource(FileSourceType.FILE, "/local/path")
    assert local_source.type == FileSourceType.FILE
    assert local_source.base_path == "/local/path"

    # HTTP file source
    http_source = FileSource(FileSourceType.HTTP, "https://example.com/docs/")
    assert http_source.type == FileSourceType.HTTP
    assert http_source.base_path == "https://example.com/docs/"


async def test_file_source_from_url_integration():
    """Test FileSource.from_url() with supported URLs."""
    # File URLs
    source = FileSource.from_url("file://./docs/guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "./docs/guide.md"

    source = FileSource.from_url("file:///docs/guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "/docs/guide.md"

    source = FileSource.from_url("file:docs/guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "docs/guide.md"

    source = FileSource.from_url("docs/guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "docs/guide.md"

    source = FileSource.from_url("/docs/guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "/docs/guide.md"

    # HTTP URLs
    source = FileSource.from_url("http://example.com/guide.md")
    assert source.type == FileSourceType.HTTP
    assert source.base_path == "http://example.com/guide.md"

    # Regular paths (no prefixes)
    source = FileSource.from_url("./docs/guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "./docs/guide.md"

    # Legacy single-colon prefixes are treated as regular paths
    source = FileSource.from_url("local:./docs/guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "local:./docs/guide.md"  # Prefix is kept as part of path
    # but we can verify they create valid sources
    source = FileSource.from_url("file:///absolute/path/guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "/absolute/path/guide.md"

    # HTTP URLs (Issue 003)
    source = FileSource.from_url("https://example.com/guide.md")
    assert source.type == FileSourceType.HTTP
    assert source.base_path == "https://example.com/guide.md"

    # Default context-aware (Issue 002)
    source = FileSource.from_url("./guide.md")
    assert source.type == FileSourceType.FILE
    assert source.base_path == "./guide.md"


async def test_file_accessor_resolve_path():
    """Test FileAccessor path resolution."""
    accessor = FileAccessor()

    # Local source
    local_source = FileSource(FileSourceType.FILE, "/client/docs")
    resolved = accessor.resolve_path("guide.md", local_source)
    assert resolved == "/client/docs/guide.md"

    # Server source
    server_source = FileSource(FileSourceType.FILE, "/server/docs")
    resolved = accessor.resolve_path("guide.md", server_source)
    assert resolved == "/server/docs/guide.md"

    # HTTP source
    http_source = FileSource(FileSourceType.HTTP, "https://example.com/docs/")
    resolved = accessor.resolve_path("guide.md", http_source)
    assert resolved == "https://example.com/docs/guide.md"


async def test_file_accessor_exists():
    """Test FileAccessor file existence checking."""
    accessor = FileAccessor()

    # HTTP source - should return True (optimistic)
    http_source = FileSource(FileSourceType.HTTP, "https://example.com/docs/")
    exists = accessor.exists("guide.md", http_source)
    assert exists is True

    # Local source - depends on actual filesystem
    local_source = FileSource(FileSourceType.FILE, "/nonexistent/path")
    exists = accessor.exists("guide.md", local_source)
    # This will be False since the path doesn't exist
    assert exists is False

    # Server source - behaves like local filesystem check
    server_source = FileSource(FileSourceType.FILE, "/nonexistent/path")
    exists = accessor.exists("guide.md", server_source)
    # This will be False since the path doesn't exist
    assert exists is False


async def test_file_source_caching_config():
    """Test FileSource caching configuration."""
    # Default caching enabled
    source = FileSource(FileSourceType.HTTP, "https://example.com/docs/")
    assert source.cache_enabled is True
    assert source.cache_ttl == 3600

    # Custom caching config
    source = FileSource(
        FileSourceType.HTTP,
        "https://example.com/docs/",
        cache_ttl=7200,
        cache_enabled=False,
    )
    assert source.cache_enabled is False
    assert source.cache_ttl == 7200


async def test_file_source_auth_headers():
    """Test FileSource authentication headers."""
    # Default no auth headers
    source = FileSource(FileSourceType.HTTP, "https://example.com/docs/")
    assert source.auth_headers == {}

    # Custom auth headers
    headers = {"Authorization": "Bearer token", "X-API-Key": "secret"}
    source = FileSource(FileSourceType.HTTP, "https://example.com/docs/", auth_headers=headers)
    assert source.auth_headers == headers


async def test_integration_with_issue_002_session():
    """Test FileSource integration with Issue 002 session paths."""
    # FileSource should integrate with session resolution
    source = FileSource.from_session_path("local:./guide.md", "test-project")
    assert source.type == FileSourceType.FILE


async def test_file_source_dataclass_behavior():
    """Test FileSource dataclass behavior."""
    # Test with required parameters
    source1 = FileSource(type=FileSourceType.FILE, base_path="/test/path")
    assert source1.type == FileSourceType.FILE
    assert source1.base_path == "/test/path"
    assert source1.cache_ttl == 3600  # default
    assert source1.cache_enabled is True  # default
    assert source1.auth_headers == {}  # default

    # Test with all parameters
    source2 = FileSource(
        type=FileSourceType.HTTP,
        base_path="https://example.com",
        cache_ttl=7200,
        cache_enabled=False,
        auth_headers={"Authorization": "Bearer token"},
    )
    assert source2.type == FileSourceType.HTTP
    assert source2.base_path == "https://example.com"
    assert source2.cache_ttl == 7200
    assert source2.cache_enabled is False
    assert source2.auth_headers == {"Authorization": "Bearer token"}


async def test_file_source_from_url():
    """Test FileSource.from_url() method."""
    # Test HTTP URL
    source1 = FileSource.from_url("https://example.com/docs")
    assert source1.type == FileSourceType.HTTP
    assert source1.base_path == "https://example.com/docs"

    # Test local path - will use context detection, so check it returns a valid source
    source2 = FileSource.from_url("/local/path")
    assert source2.type in [FileSourceType.FILE, FileSourceType.HTTP]  # Any valid type
    assert source2.base_path == "/local/path"

    # Test unsupported prefix - should raise ValueError
    with pytest.raises(ValueError, match="Unsupported URL scheme: badprefix://"):
        FileSource.from_url("badprefix://some/path")


async def test_file_source_comprehensive():
    """Test comprehensive FileSource functionality."""
    # Test different source types
    local_source = FileSource(type=FileSourceType.FILE, base_path="/docs")
    assert local_source.type == FileSourceType.FILE

    http_source = FileSource(type=FileSourceType.HTTP, base_path="https://api.example.com")
    assert http_source.type == FileSourceType.HTTP

    server_source = FileSource(type=FileSourceType.FILE, base_path="internal/path")
    assert server_source.type == FileSourceType.FILE

    # Test cache settings
    assert local_source.cache_enabled is True
    assert http_source.cache_ttl == 3600
