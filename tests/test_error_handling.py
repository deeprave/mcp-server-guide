"""Tests for error handling framework."""

import logging
from unittest.mock import Mock
from mcp_server_guide.exceptions import (
    MCPError,
    ValidationError,
    SecurityError,
    ConfigurationError,
    ErrorResponse,
    SuccessResponse,
)
from mcp_server_guide.error_handler import ErrorHandler, handle_errors


class TestMCPExceptions:
    """Test custom exception classes."""

    def test_mcp_error_basic(self):
        """Test basic MCPError functionality."""
        error = MCPError("Test error")
        assert str(error) == "Test error"
        assert error.error_code == "MCPError"
        assert error.context == {}
        assert error.timestamp is not None

    def test_mcp_error_with_context(self):
        """Test MCPError with custom error code and context."""
        context = {"user_id": "123", "operation": "test"}
        error = MCPError("Test error", error_code="CUSTOM_ERROR", context=context)

        assert str(error) == "Test error"
        assert error.error_code == "CUSTOM_ERROR"
        assert error.context == context

    def test_specific_error_types(self):
        """Test specific error type inheritance."""
        validation_error = ValidationError("Invalid input")
        security_error = SecurityError("Access denied")
        config_error = ConfigurationError("Config missing")

        assert isinstance(validation_error, MCPError)
        assert isinstance(security_error, MCPError)
        assert isinstance(config_error, MCPError)

        assert validation_error.error_code == "ValidationError"
        assert security_error.error_code == "SecurityError"
        assert config_error.error_code == "ConfigurationError"


class TestErrorResponse:
    """Test error response formatting."""

    def test_error_response_from_mcp_error(self):
        """Test creating ErrorResponse from MCPError."""
        context = {"field": "username"}
        error = ValidationError("Invalid username", context=context)

        response = ErrorResponse.from_exception(error, "user_validation")

        assert response.success is False
        assert response.error_code == "ValidationError"
        assert response.message == "Invalid username"
        assert response.context["field"] == "username"
        assert response.context["operation"] == "user_validation"
        assert response.timestamp is not None

    def test_error_response_from_standard_exception(self):
        """Test creating ErrorResponse from standard exception."""
        error = ValueError("Invalid value")

        response = ErrorResponse.from_exception(error, "data_processing")

        assert response.success is False
        assert response.error_code == "UnexpectedError"
        assert response.message == "An unexpected error occurred"
        assert response.context["operation"] == "data_processing"
        assert response.context["error_type"] == "ValueError"

    def test_success_response(self):
        """Test success response creation."""
        data = {"result": "success"}
        response = SuccessResponse(data=data, message="Operation completed")

        assert response.success is True
        assert response.data == data
        assert response.message == "Operation completed"
        assert response.timestamp is not None


class TestErrorHandler:
    """Test error handler functionality."""

    def test_error_handler_with_mcp_error(self):
        """Test error handler with MCPError."""
        mock_logger = Mock(spec=logging.Logger)
        handler = ErrorHandler(mock_logger)

        error = ValidationError("Invalid input", context={"field": "email"})
        response = handler.handle_error(error, "email_validation")

        # Check logging
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert "email_validation failed" in call_args[0][0]
        assert call_args[1]["extra"]["error_code"] == "ValidationError"
        assert call_args[1]["extra"]["field"] == "email"

        # Check response
        assert isinstance(response, ErrorResponse)
        assert response.error_code == "ValidationError"
        assert response.context["operation"] == "email_validation"

    def test_error_handler_with_standard_exception(self):
        """Test error handler with standard exception."""
        mock_logger = Mock(spec=logging.Logger)
        handler = ErrorHandler(mock_logger)

        error = RuntimeError("Unexpected error")
        response = handler.handle_error(error, "data_processing")

        # Check logging
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "Unexpected error in data_processing" in call_args[0][0]
        assert call_args[1]["exc_info"] is True

        # Check response
        assert isinstance(response, ErrorResponse)
        assert response.error_code == "UnexpectedError"

    def test_create_success_response(self):
        """Test success response creation."""
        handler = ErrorHandler()

        data = {"users": [1, 2, 3]}
        response = handler.create_success_response(data, "Users retrieved")

        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.data == data
        assert response.message == "Users retrieved"

    def test_wrap_operation_success(self):
        """Test operation wrapper with successful operation."""
        handler = ErrorHandler()

        @handler.wrap_operation("test_operation")
        def successful_operation():
            return {"result": "success"}

        response = successful_operation()

        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.data == {"result": "success"}

    def test_wrap_operation_error(self):
        """Test operation wrapper with failing operation."""
        mock_logger = Mock(spec=logging.Logger)
        handler = ErrorHandler(mock_logger)

        @handler.wrap_operation("test_operation")
        def failing_operation():
            raise ValidationError("Test error")

        response = failing_operation()

        assert isinstance(response, ErrorResponse)
        assert response.success is False
        assert response.error_code == "ValidationError"
        mock_logger.warning.assert_called_once()

    def test_wrap_operation_returns_response_as_is(self):
        """Test that wrapper doesn't double-wrap response objects."""
        handler = ErrorHandler()

        @handler.wrap_operation("test_operation")
        def operation_returning_response():
            return ErrorResponse(error_code="CUSTOM", message="Custom error")

        response = operation_returning_response()

        assert isinstance(response, ErrorResponse)
        assert response.error_code == "CUSTOM"
        assert response.message == "Custom error"


class TestHandleErrorsDecorator:
    """Test the convenience decorator."""

    def test_handle_errors_decorator_success(self):
        """Test handle_errors decorator with successful operation."""

        @handle_errors("test_operation")
        def successful_function():
            return "success"

        response = successful_function()

        assert isinstance(response, SuccessResponse)
        assert response.data == "success"

    def test_handle_errors_decorator_error(self):
        """Test handle_errors decorator with error."""

        @handle_errors("test_operation")
        def failing_function():
            raise ValueError("Test error")

        response = failing_function()

        assert isinstance(response, ErrorResponse)
        assert response.error_code == "UnexpectedError"


class TestErrorHandlingIntegration:
    """Test error handling integration scenarios."""

    def test_error_propagation_chain(self):
        """Test error propagation through multiple layers."""

        @handle_errors("layer_1")
        def layer_1():
            return layer_2()

        @handle_errors("layer_2")
        def layer_2():
            raise ValidationError("Deep error", context={"layer": "2"})

        response = layer_1()

        assert isinstance(response, ErrorResponse)
        assert response.error_code == "ValidationError"
        assert response.message == "Deep error"
        assert response.context["layer"] == "2"

    def test_error_context_preservation(self):
        """Test that error context is preserved through handling."""
        original_context = {"user_id": "123", "action": "delete"}
        error = SecurityError("Access denied", context=original_context)

        handler = ErrorHandler()
        response = handler.handle_error(error, "user_deletion")

        assert response.context["user_id"] == "123"
        assert response.context["action"] == "delete"
        assert response.context["operation"] == "user_deletion"
