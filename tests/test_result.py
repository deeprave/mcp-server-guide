"""Tests for Result class."""

import json
from typing import Any

import pytest

from mcp_server_guide.utils.result import Result


def test_result_ok_creates_success() -> None:
    """Test Result.ok() creates successful result."""
    result = Result.ok("test value")

    assert result.success is True
    assert result.value == "test value"
    assert result.error is None
    assert result.error_type is None


def test_result_failure_creates_error() -> None:
    """Test Result.failure() creates error result."""
    result: Result[Any] = Result.failure("test error", error_type="validation")

    assert result.success is False
    assert result.error == "test error"
    assert result.error_type == "validation"
    assert result.value is None


def test_result_is_ok() -> None:
    """Test is_ok() returns correct boolean."""
    assert Result.ok("value").is_ok() is True
    assert Result.failure("error").is_ok() is False


def test_result_is_failure() -> None:
    """Test is_failure() returns correct boolean."""
    assert Result.ok("value").is_failure() is False
    assert Result.failure("error").is_failure() is True


def test_result_to_json_success_with_value() -> None:
    """Test to_json() for success with value."""
    result = Result.ok("content here")
    json_output = result.to_json()

    assert json_output == {"success": True, "value": "content here"}


def test_result_to_json_success_with_message() -> None:
    """Test to_json() for success with message."""
    result = Result.ok(None)
    result.message = "Operation completed"
    json_output = result.to_json()

    assert json_output == {"success": True, "message": "Operation completed"}


def test_result_to_json_success_with_instruction() -> None:
    """Test to_json() for success with instruction."""
    result = Result.ok("display content")
    result.instruction = "Present this to user"
    json_output = result.to_json()

    assert json_output == {"success": True, "value": "display content", "instruction": "Present this to user"}


def test_result_to_json_failure_basic() -> None:
    """Test to_json() for basic failure."""
    result: Result[str] = Result.failure("Something went wrong", error_type="unknown")
    json_output = result.to_json()

    assert json_output == {"success": False, "error": "Something went wrong", "error_type": "unknown"}


def test_result_to_json_failure_with_instruction() -> None:
    """Test to_json() for failure with instruction."""
    result: Result[str] = Result.failure("Project not found", error_type="project_context")
    result.instruction = "Call switch_project to set context"
    json_output = result.to_json()

    assert json_output == {
        "success": False,
        "error": "Project not found",
        "error_type": "project_context",
        "instruction": "Call switch_project to set context",
    }


def test_result_to_json_failure_with_exception() -> None:
    """Test to_json() includes exception details."""
    exc = ValueError("Invalid input")
    result: Result[str] = Result.failure("Validation failed", error_type="validation", exception=exc)
    json_output = result.to_json()

    assert json_output["success"] is False
    assert json_output["error"] == "Validation failed"
    assert json_output["error_type"] == "validation"
    assert json_output["exception_type"] == "ValueError"
    assert json_output["exception_message"] == "Invalid input"


def test_result_to_json_omits_none_values() -> None:
    """Test to_json() doesn't include None values."""
    result = Result.ok(None)
    json_output = result.to_json()

    assert json_output == {"success": True}
    assert "value" not in json_output
    assert "message" not in json_output
    assert "instruction" not in json_output


def test_result_failure_default_error_type() -> None:
    """Test Result.failure() defaults to error_type='unknown'."""
    result: Result[str] = Result.failure("some error")

    assert result.success is False
    assert result.error == "some error"
    assert result.error_type == "unknown"


def test_result_failure_default_error_type_in_json() -> None:
    """Test to_json() includes default error_type='unknown'."""
    result: Result[str] = Result.failure("some error")
    json_output = result.to_json()

    assert json_output == {
        "success": False,
        "error": "some error",
        "error_type": "unknown",
    }
    assert "exception_type" not in json_output
    assert "exception_message" not in json_output


def test_result_to_json_str_helper() -> None:
    """Test to_json_str() helper method."""
    result = Result.ok("test value")
    json_str = result.to_json_str()

    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["success"] is True
    assert parsed["value"] == "test value"


# Tests for Generic[T] behavior


def test_result_ok_with_dict_value() -> None:
    """Test Result.ok() with dict value."""
    data = {"key": "value", "count": 42}
    result = Result.ok(data)

    assert result.success is True
    assert result.value == data
    assert result.value["key"] == "value"
    assert result.value["count"] == 42


def test_result_ok_with_list_value() -> None:
    """Test Result.ok() with list value."""
    items = ["item1", "item2", "item3"]
    result = Result.ok(items)

    assert result.success is True
    assert result.value == items
    assert len(result.value) == 3


def test_result_ok_with_custom_object() -> None:
    """Test Result.ok() with custom object."""

    class CustomObject:
        def __init__(self, name: str):
            self.name = name

    obj = CustomObject("test")
    result = Result.ok(obj)

    assert result.success is True
    assert result.value is not None
    assert result.value.name == "test"


def test_result_to_json_with_dict_value() -> None:
    """Test to_json() preserves dict values."""
    data = {"nested": {"key": "value"}}
    result = Result.ok(data)
    json_output = result.to_json()

    assert json_output["success"] is True
    assert json_output["value"] == data
