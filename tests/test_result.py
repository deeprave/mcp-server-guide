"""Tests for Result class."""

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
    result = Result.failure("test error", error_type="validation")

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
    result = Result.failure("Something went wrong", error_type="unknown")
    json_output = result.to_json()

    assert json_output == {"success": False, "error": "Something went wrong", "error_type": "unknown"}


def test_result_to_json_failure_with_instruction() -> None:
    """Test to_json() for failure with instruction."""
    result = Result.failure("Project not found", error_type="project_context")
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
    result = Result.failure("Validation failed", error_type="validation", exception=exc)
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
