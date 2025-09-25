"""Tests for file source abstraction (Issue 003 Phase 1)."""

from mcpguide.file_source import FileSource, FileAccessor


def test_file_source_creation():
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


def test_file_source_from_url_integration():
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


def test_file_accessor_resolve_path():
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


def test_file_accessor_file_exists():
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


def test_file_accessor_read_file():
    """Test FileAccessor reads files."""
    accessor = FileAccessor()

    # Local file reading
    local_source = FileSource("local", ".")
    content = accessor.read_file("README.md", local_source)
    assert isinstance(content, str)
    assert len(content) > 0

    # Server file reading
    server_source = FileSource("server", ".")
    content = accessor.read_file("README.md", server_source)
    assert isinstance(content, str)
    assert len(content) > 0


def test_file_source_context_detection():
    """Test context detection for deployment mode."""
    # Should detect local vs server deployment
    context = FileSource.detect_deployment_context()
    assert context in ["local", "server"]

    # Should provide appropriate default
    default_source = FileSource.get_context_default("./guide.md")
    assert default_source.type in ["local", "server"]


def test_integration_with_issue_002_session():
    """Test integration with Issue 002 session system."""
    from mcpguide.session import resolve_session_path

    # Should be able to resolve Issue 002 session paths
    resolved = resolve_session_path("local:./guide.md", "test-project")
    assert resolved.endswith("guide.md")

    # FileSource should integrate with session resolution
    source = FileSource.from_session_path("local:./guide.md", "test-project")
    assert source.type == "local"
