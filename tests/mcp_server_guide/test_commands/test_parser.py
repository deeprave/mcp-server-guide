"""Tests for command parser functionality."""
from unittest.mock import patch

from mcp_server_guide.commands.parser import CommandParser


def test_parse_basic_slash_command():
    """Test parsing basic command."""
    parser = CommandParser()
    result = parser.parse_command("guide")

    assert result is not None
    assert result["command"] == "guide"
    assert result["args"] == []


def test_parse_command_with_arguments():
    """Test parsing command with arguments."""
    parser = CommandParser()
    result = parser.parse_command("guide lang")

    assert result is not None
    assert result["command"] == "guide"
    assert result["args"] == ["lang"]



def test_parse_empty_command():
    """Test parsing empty or whitespace command."""
    parser = CommandParser()

    assert parser.parse_command("") is None
    assert parser.parse_command("   ") is None


def test_parse_command_shlex_failure():
    """Test parsing command when shlex.split fails due to unmatched quotes."""
    parser = CommandParser()

    # Test cases that cause shlex.split to raise ValueError
    test_cases = [
        'guide "unmatched quote',
        "guide 'unmatched single quote",
        'guide "nested "quotes" problem',
        "guide 'mixed \"quotes problem",
    ]

    # sourcery skip: no-loop-in-tests
    for test_case in test_cases:
        result = parser.parse_command(test_case)
        assert result is None, f"Expected None for malformed input: {test_case}"


def test_parse_command_boolean():  # sourcery skip: extract-duplicate-method
    parser = CommandParser()

    result = parser.parse_command("guide test=1 verbose=true")
    assert "params" in result
    assert result["params"]["test"] == "1"
    assert result["params"]["verbose"] is True

    result = parser.parse_command("guide test=2 verbose=false")
    assert "params" in result
    assert result["params"]["test"] == "2"
    assert result["params"]["verbose"] is False


def test_parse_command_args():  # sourcery skip: extract-duplicate-method
    parser = CommandParser()

    result = parser.parse_command("guide one,two,three")
    assert "args" in result
    assert result["args"] == ["one,two,three"]


def test_parse_parameter_csv_fallback():
    import csv
    """Test parameter parsing when csv.reader fails and falls back to simple split."""
    parser = CommandParser()

    # Mock csv.reader to raise csv.Error to test the fallback
    with patch('csv.reader') as mock_reader:
        mock_reader.side_effect = csv.Error("Mocked CSV error")

        result = parser.parse_command('guide list="item1,item2,item3"')

        assert result is not None
        assert result["command"] == "guide"
        assert "list" in result["params"]
        # Should fall back to simple split
        assert result["params"]["list"] == ["item1", "item2", "item3"]

def test_parse_command_csv():  # sourcery skip: extract-duplicate-method
    parser = CommandParser()

    result = parser.parse_command("guide list=one,two,three")
    assert "params" in result
    assert "list" in result["params"]
    assert result["params"]["list"] == ["one" ,"two", "three"]


def test_natural_language_passthrough():
    """Test that natural language passes through without being parsed."""
    parser = CommandParser()

    # These should return None to let AI handle them
    assert parser.parse_command("please guide me") is None
    assert parser.parse_command("can you guide me") is None
    assert parser.parse_command("I need guidance") is None


def test_command_parsed():
    parser = CommandParser()

    result = parser.parse_command("guide me through this process")
    assert result is not None
    assert result["command"] == "guide"
    assert result["args"] == ["me", "through", "this", "process"]

    result = parser.parse_command("guide me step by step")
    assert result is not None
    assert result["command"] == "guide"
    assert result["args"] == ["me", "step", "by", "step"]
