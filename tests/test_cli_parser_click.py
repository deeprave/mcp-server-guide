"""Tests for Click-based CLI parser."""

from src.mcp_server_guide.cli_parser_click import parse_command, generate_cli_help, generate_context_help


class TestClickCommandParser:
    """Test Click-based command parser."""

    def test_help_command(self):
        """Test help command parsing."""
        result = parse_command(["--help"])
        assert result.type == "help"
        assert result.target is None

    def test_phase_commands(self):
        """Test phase command parsing."""
        # Test discuss
        result = parse_command(["discuss", "some", "text"])
        assert result.type == "discuss"
        assert result.data == "some text"

        # Test plan
        result = parse_command(["plan"])
        assert result.type == "plan"
        assert result.data is None

        # Test implement with text
        result = parse_command(["implement", "feature", "xyz"])
        assert result.type == "implement"
        assert result.data == "feature xyz"

    def test_category_commands(self):
        """Test category command parsing."""
        # Test category list
        result = parse_command(["category", "list"])
        assert result.type == "crud"
        assert result.target == "category"
        assert result.operation == "list"
        assert result.data["verbose"] is False

        # Test category list verbose
        result = parse_command(["category", "list", "--verbose"])
        assert result.data["verbose"] is True

        # Test category add
        result = parse_command(["category", "add", "test-cat", "*.py", "*.js"])
        assert result.type == "crud"
        assert result.target == "category"
        assert result.operation == "add"
        assert result.data["name"] == "test-cat"
        assert result.data["patterns"] == ["*.py", "*.js"]

        # Test category add with description
        result = parse_command(["category", "add", "test-cat", "*.py", "--description", "Test category"])
        assert result.data["description"] == "Test category"

    def test_collection_commands(self):
        """Test collection command parsing."""
        # Test collection list
        result = parse_command(["collection", "list"])
        assert result.type == "crud"
        assert result.target == "collection"
        assert result.operation == "list"

        # Test collection add
        result = parse_command(["collection", "add", "test-coll", "cat1", "cat2"])
        assert result.type == "crud"
        assert result.target == "collection"
        assert result.operation == "add"
        assert result.data["name"] == "test-coll"
        assert result.data["categories"] == ["cat1", "cat2"]

    def test_document_commands(self):
        """Test document command parsing."""
        # Test document list
        result = parse_command(["document", "list"])
        assert result.type == "crud"
        assert result.target == "document"
        assert result.operation == "list"

        # Test document create
        result = parse_command(["document", "create", "test.md", "# Test Content"])
        assert result.type == "crud"
        assert result.target == "document"
        assert result.operation == "create"
        assert result.data["name"] == "test.md"
        assert result.data["content"] == "# Test Content"

    def test_help_generation(self):
        """Test help generation functions."""
        # Test general help generation
        help_text = generate_cli_help()
        assert "MCP Server Guide" in help_text
        assert "Commands:" in help_text

        # Test context-sensitive help
        category_help = generate_context_help("category")
        assert "Category management" in category_help

        collection_help = generate_context_help("collection")
        assert "Collection management" in collection_help

        document_help = generate_context_help("document")
        assert "Document management" in document_help

    def test_invalid_commands(self):
        """Test handling of invalid commands."""
        # Invalid command should return help
        result = parse_command(["invalid", "command"])
        assert result.type == "help"

    def test_empty_args(self):
        """Test handling of empty arguments."""
        result = parse_command([])
        assert result.type == "help"
