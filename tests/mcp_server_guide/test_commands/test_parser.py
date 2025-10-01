"""Tests for command parser functionality."""

from mcp_server_guide.commands.parser import CommandParser


def test_parse_basic_slash_command():
    """Test parsing basic slash command."""
    parser = CommandParser()
    result = parser.parse_command("/guide")

    assert result is not None
    assert result["command"] == "guide"
    assert result["args"] == []


def test_parse_command_with_arguments():
    """Test parsing command with arguments."""
    parser = CommandParser()
    result = parser.parse_command("/guide lang")

    assert result is not None
    assert result["command"] == "guide"
    assert result["args"] == ["lang"]


def test_parse_invalid_non_slash_command():
    """Test that non-slash commands return None."""
    parser = CommandParser()
    result = parser.parse_command("guide")

    assert result is None


def test_parse_empty_command():
    """Test parsing empty or whitespace command."""
    parser = CommandParser()

    assert parser.parse_command("") is None
    assert parser.parse_command("   ") is None
    assert parser.parse_command("/") is None


def test_parse_key_value_parameters():
    """Test parsing key=value parameters."""
    parser = CommandParser()
    result = parser.parse_command("/guide-new typescript dir=lang/ts")

    assert result is not None
    assert result["command"] == "guide-new"
    assert result["args"] == ["typescript"]
    assert result["params"] == {"dir": "lang/ts"}


def test_parse_comma_separated_values():
    """Test parsing comma-separated values."""
    parser = CommandParser()
    result = parser.parse_command("/guide-new typescript patterns=*.ts,*.tsx")

    assert result is not None
    assert result["params"] == {"patterns": ["*.ts", "*.tsx"]}


def test_parse_boolean_parameters():
    """Test parsing boolean parameters."""
    parser = CommandParser()
    result = parser.parse_command("/guide-new typescript auto-load=true")

    assert result is not None
    assert result["params"] == {"auto-load": True}

    result = parser.parse_command("/guide-new typescript auto-load=false")
    assert result["params"] == {"auto-load": False}


def test_parse_mixed_parameters():
    """Test parsing mixed parameter types."""
    parser = CommandParser()
    result = parser.parse_command("/guide-new typescript dir=lang/ts patterns=*.ts,*.tsx auto-load=true")

    assert result is not None
    assert result["command"] == "guide-new"
    assert result["args"] == ["typescript"]
    assert result["params"] == {"dir": "lang/ts", "patterns": ["*.ts", "*.tsx"], "auto-load": True}


def test_parse_colon_syntax_guide_category():
    """Test parsing /guide:category syntax."""
    parser = CommandParser()
    result = parser.parse_command("/guide:lang")

    assert result is not None
    assert result["command"] == "guide"
    assert result["subcommand"] == "lang"
    assert result["args"] == []


def test_parse_colon_syntax_g_shorthand():
    """Test parsing /g:category syntax."""
    parser = CommandParser()
    result = parser.parse_command("/g:lang")

    assert result is not None
    assert result["command"] == "g"
    assert result["subcommand"] == "lang"
    assert result["args"] == []


def test_parse_colon_syntax_with_params():
    """Test parsing colon syntax with parameters."""
    parser = CommandParser()
    result = parser.parse_command("/guide:new typescript dir=lang/ts patterns=*.ts,*.tsx")

    assert result is not None
    assert result["command"] == "guide"
    assert result["subcommand"] == "new"
    assert result["args"] == ["typescript"]
    assert result["params"] == {"dir": "lang/ts", "patterns": ["*.ts", "*.tsx"]}


def test_parse_g_shorthand_with_params():
    """Test parsing /g shorthand with parameters."""
    parser = CommandParser()
    result = parser.parse_command("/g:edit typescript patterns=*.ts,*.tsx,*.d.ts")

    assert result is not None
    assert result["command"] == "g"
    assert result["subcommand"] == "edit"
    assert result["args"] == ["typescript"]
    assert result["params"] == {"patterns": ["*.ts", "*.tsx", "*.d.ts"]}


def test_parse_help_commands():
    """Test parsing help commands."""
    parser = CommandParser()

    result = parser.parse_command("/guide:help")
    assert result is not None
    assert result["command"] == "guide"
    assert result["subcommand"] == "help"

    result = parser.parse_command("/g:help")
    assert result is not None
    assert result["command"] == "g"
    assert result["subcommand"] == "help"


def test_parse_quoted_arguments():
    """Test parsing commands with quoted arguments."""
    parser = CommandParser()

    # Test quoted directory path with spaces
    result = parser.parse_command('/guide-new "my project" dir="my docs/typescript"')
    assert result is not None
    assert result["command"] == "guide-new"
    assert result["args"] == ["my project"]
    assert result["params"] == {"dir": "my docs/typescript"}

    # Test quoted patterns
    result = parser.parse_command('/guide:new typescript patterns="*.ts,*.tsx" dir="lang/ts with spaces"')
    assert result is not None
    assert result["command"] == "guide"
    assert result["subcommand"] == "new"
    assert result["args"] == ["typescript"]
    assert result["params"] == {"patterns": ["*.ts", "*.tsx"], "dir": "lang/ts with spaces"}
