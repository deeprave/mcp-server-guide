"""Tests for file source abstraction (Issue 003 Phase 1)."""

from mcp_server_guide.file_source import FileSource, FileAccessor


async def test_file_source_creation():
    """Test creating file sources."""
    # Local file source
    local_source = FileSource("local", "/client/path")
    assert local_source.type == "local"
    assert local_source.base_path == "/client/path"
    assert local_source.cache_enabled is True
    assert local_source.cache_ttl == 3600

    # Server file source
    server_source = FileSource("server", "/server/path")
    assert server_source.type == "server"
    assert server_source.base_path == "/server/path"

    # HTTP file source
    http_source = FileSource("http", "https://example.com/docs/")
    assert http_source.type == "http"
    assert http_source.base_path == "https://example.com/docs/"


async def test_file_source_from_url_integration():
    """Test FileSource.from_url() integrates with Issue 002 URLs."""
    # Local prefix (Issue 002)
    source = FileSource.from_url("local:./docs/guide.md")
    assert source.type == "local"
    assert source.base_path == "./docs/guide.md"

    # Server prefix (Issue 002)
    source = FileSource.from_url("server:./docs/guide.md")
    assert source.type == "server"
    assert source.base_path == "./docs/guide.md"

    # File URLs (Issue 002)
    source = FileSource.from_url("file://./guide.md")
    assert source.type in ["local", "server"]  # Context-aware

    source = FileSource.from_url("file:///abs/guide.md")
    assert source.type in ["local", "server"]  # Context-aware

    # HTTP URLs (Issue 003)
    source = FileSource.from_url("https://example.com/guide.md")
    assert source.type == "http"
    assert source.base_path == "https://example.com/guide.md"

    # Default context-aware (Issue 002)
    source = FileSource.from_url("./guide.md")
    assert source.type in ["local", "server"]  # Context-aware


async def test_file_accessor_resolve_path():
    """Test FileAccessor resolves paths correctly."""
    accessor = FileAccessor()

    # Local source
    local_source = FileSource("local", "/client/docs")
    resolved = accessor.resolve_path("guide.md", local_source)
    assert resolved == "/client/docs/guide.md"

    # Server source
    server_source = FileSource("server", "/server/docs")
    resolved = accessor.resolve_path("guide.md", server_source)
    assert resolved == "/server/docs/guide.md"

    # HTTP source
    http_source = FileSource("http", "https://example.com/docs/")
    resolved = accessor.resolve_path("guide.md", http_source)
    assert resolved == "https://example.com/docs/guide.md"


async def test_file_accessor_file_exists():
    """Test FileAccessor checks file existence."""
    accessor = FileAccessor()

    # Local file existence (should work)
    local_source = FileSource("local", ".")
    exists = accessor.file_exists("README.md", local_source)
    assert isinstance(exists, bool)

    # Server file existence (should work)
    server_source = FileSource("server", ".")
    exists = accessor.file_exists("README.md", server_source)
    assert isinstance(exists, bool)

    # HTTP file existence (now works in Phase 2)
    http_source = FileSource("http", "https://example.com/")
    exists = accessor.file_exists("guide.md", http_source)
    assert isinstance(exists, bool)  # Should return boolean (likely False for non-existent URL)


async def test_file_accessor_read_file():
    """Test FileAccessor reads files."""
    accessor = FileAccessor()

    # Create a test file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test Content")
        test_file = f.name

    try:
        # Local file reading
        local_source = FileSource("local", ".")
        content = await accessor.read_file(test_file, local_source)
        assert isinstance(content, str)
        assert "Test Content" in content
    finally:
        import os

        os.unlink(test_file)

    # Server file reading - use the same test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f2:
        f2.write("# Server Test Content")
        test_file2 = f2.name

    try:
        server_source = FileSource("server", ".")
        content = await accessor.read_file(test_file2, server_source)
        assert isinstance(content, str)
        assert "Server Test Content" in content
    finally:
        import os

        os.unlink(test_file2)


async def test_file_source_context_detection():
    """Test context detection for deployment mode."""
    # Should detect local vs server deployment
    context = FileSource.detect_deployment_context()
    assert context in ["local", "server"]

    # Should provide appropriate default
    default_source = FileSource.get_context_default("./guide.md")
    assert default_source.type in ["local", "server"]


async def test_integration_with_issue_002_session():
    """Test integration with Issue 002 session system."""
    from mcp_server_guide.session import resolve_session_path

    # Should be able to resolve Issue 002 session paths
    resolved = resolve_session_path("local:./guide.md", "test-project")
    assert resolved.endswith("guide.md")

    # FileSource should integrate with session resolution
    source = FileSource.from_session_path("local:./guide.md", "test-project")
    assert source.type == "local"


async def test_file_source_initialization():
    """Test file source initialization."""
    # Test with required parameters
    source1 = FileSource(type="local", base_path="/test/path")
    assert source1.type == "local"
    assert source1.base_path == "/test/path"
    assert source1.cache_ttl == 3600  # default

    # Test with all parameters
    source2 = FileSource(
        type="http",
        base_path="https://example.com",
        cache_ttl=7200,
        cache_enabled=False,
        auth_headers={"Authorization": "Bearer token"},
    )
    assert source2.type == "http"
    assert source2.base_path == "https://example.com"
    assert source2.cache_ttl == 7200
    assert source2.cache_enabled is False
    assert source2.auth_headers == {"Authorization": "Bearer token"}


async def test_file_source_from_url():
    """Test FileSource.from_url class method."""
    # Test HTTP URL
    source1 = FileSource.from_url("https://example.com/docs")
    assert source1.type == "http"
    assert source1.base_path == "https://example.com/docs"

    # Test local path - will use context detection, so check it returns a valid source
    source2 = FileSource.from_url("/local/path")
    assert source2.type in ["local", "server", "http"]  # Any valid type
    assert source2.base_path == "/local/path"


async def test_file_source_comprehensive():
    """Test file source comprehensive functionality."""
    # Test different source types
    local_source = FileSource(type="local", base_path="/docs")
    assert local_source.type == "local"

    http_source = FileSource(type="http", base_path="https://api.example.com")
    assert http_source.type == "http"

    server_source = FileSource(type="server", base_path="server://internal")
    assert server_source.type == "server"

    # Test cache settings
    cached_source = FileSource(type="local", base_path="/cache", cache_enabled=True, cache_ttl=1800)
    assert cached_source.cache_enabled is True
    assert cached_source.cache_ttl == 1800

    no_cache_source = FileSource(type="local", base_path="/nocache", cache_enabled=False)
    assert no_cache_source.cache_enabled is False
