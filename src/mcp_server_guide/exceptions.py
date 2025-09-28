"""Custom exceptions for MCP server guide."""

from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


class MCPError(Exception):
    """Base exception for all MCP server errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)


class ValidationError(MCPError):
    """Input validation failures."""

    pass


class SecurityError(MCPError):
    """Security policy violations."""

    pass


class ConfigurationError(MCPError):
    """Configuration loading/parsing errors."""

    pass


class FileAccessError(MCPError):
    """File system access errors."""

    pass


class NetworkError(MCPError):
    """Network-related errors."""

    pass


class ToolExecutionError(MCPError):
    """Tool execution failures."""

    pass


@dataclass
class ErrorResponse:
    """Standardized error response format."""

    success: bool = False
    error_code: str = ""
    message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    @classmethod
    def from_exception(cls, error: Exception, operation: str = "") -> "ErrorResponse":
        """Create ErrorResponse from an exception."""
        if isinstance(error, MCPError):
            return cls(
                error_code=error.error_code,
                message=str(error),
                context={**error.context, "operation": operation} if operation else error.context,
                timestamp=error.timestamp.isoformat(),
            )
        else:
            return cls(
                error_code="UnexpectedError",
                message="An unexpected error occurred",
                context={"operation": operation, "error_type": type(error).__name__}
                if operation
                else {"error_type": type(error).__name__},
                timestamp=datetime.now(timezone.utc).isoformat(),
            )


@dataclass
class SuccessResponse:
    """Standardized success response format."""

    success: bool = True
    data: Any = None
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
