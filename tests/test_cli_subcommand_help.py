"""Test for CRUD sub-command help detection bug."""

from src.mcp_server_guide.cli_parser_click import parse_command


def test_category_add_help():
    """Test that ':category add --help' shows help."""
    result = parse_command([":category", "add", "--help"])
    # Click handles --help and exits, we catch it and return help
    assert result.type == "help", f"Expected help, got {result.type}"


def test_collection_add_help():
    """Test that ':collection add --help' shows help."""
    result = parse_command([":collection", "add", "--help"])
    assert result.type == "help"


def test_document_create_help():
    """Test that ':document create --help' shows help."""
    result = parse_command([":document", "create", "--help"])
    assert result.type == "help"


def test_help_flag_anywhere():
    """Test that --help is detected anywhere in args."""
    # At end
    result = parse_command([":category", "update", "test", "--help"])
    assert result.type == "help"

    # In middle
    result = parse_command([":category", "--help", "add"])
    assert result.type == "help"
