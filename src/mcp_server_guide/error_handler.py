"""Error handling utilities for consistent error management."""

import logging
from typing import Any, Union, Optional, Callable
from .exceptions import MCPError, ErrorResponse, SuccessResponse


class ErrorHandler:
    """Centralized error handling and response formatting."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def handle_error(self, error: Exception, operation: str = "") -> ErrorResponse:
        """Handle an error and return standardized response.

        Args:
            error: The exception that occurred
            operation: Description of the operation that failed

        Returns:
            Standardized error response
        """
        if isinstance(error, MCPError):
            # Log MCP errors as warnings with context
            self.logger.warning(
                f"{operation} failed: {error}",
                extra={"error_code": error.error_code, "operation": operation, **error.context},
            )
        else:
            # Log unexpected errors with full traceback
            self.logger.error(
                f"Unexpected error in {operation}: {error}", exc_info=True, extra={"operation": operation}
            )

        return ErrorResponse.from_exception(error, operation)

    def create_success_response(self, data: Any = None, message: str = "") -> SuccessResponse:
        """Create a standardized success response.

        Args:
            data: Response data
            message: Success message

        Returns:
            Standardized success response
        """
        return SuccessResponse(data=data, message=message)

    def wrap_operation(self, operation_name: str) -> Callable:
        """Decorator to wrap operations with error handling.

        Args:
            operation_name: Name of the operation for logging

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            def wrapper(*args: Any, **kwargs: Any) -> Union[ErrorResponse, SuccessResponse]:
                try:
                    result = func(*args, **kwargs)
                    # If result is already a response object, return as-is
                    if isinstance(result, (ErrorResponse, SuccessResponse)):
                        return result
                    # Otherwise wrap in success response
                    return self.create_success_response(data=result)
                except Exception as e:
                    return self.handle_error(e, operation_name)

            return wrapper

        return decorator


# Global error handler instance
default_error_handler = ErrorHandler()


def handle_errors(operation_name: str) -> Callable:
    """Convenience decorator for error handling.

    Args:
        operation_name: Name of the operation for logging

    Returns:
        Decorator function
    """
    return default_error_handler.wrap_operation(operation_name)
