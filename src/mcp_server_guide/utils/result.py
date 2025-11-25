"""Result pattern for rich error handling."""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    """Result pattern for rich error handling.

    Generic result type that can hold any value type.
    """

    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    exception: Optional[Exception] = field(default=None, repr=False, compare=False)
    message: Optional[str] = None
    instruction: Optional[str] = None

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        """Create a successful result."""
        return cls(success=True, value=value)

    @classmethod
    def failure(cls, error: str, error_type: str = "unknown", exception: Optional[Exception] = None) -> "Result[T]":
        """Create a failure result with error information."""
        return cls(success=False, error=error, error_type=error_type, exception=exception)

    def is_ok(self) -> bool:
        """Check if result is successful."""
        return self.success

    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return not self.success

    def to_json(self) -> Dict[str, Any]:
        """Convert to MCP-compatible JSON format."""
        if self.success:
            result: Dict[str, Any] = {"success": True}
            if self.value is not None:
                result["value"] = self.value
        else:
            result = {
                "success": False,
                "error": self.error,
                "error_type": self.error_type,
            }
            # Include exception details for debugging
            if self.exception:
                result["exception_type"] = type(self.exception).__name__
                result["exception_message"] = str(self.exception)

        if self.message:
            result["message"] = self.message
        if self.instruction:
            result["instruction"] = self.instruction

        return result

    def to_json_str(self) -> str:
        """Convert to JSON string for MCP tool responses."""
        return json.dumps(self.to_json())
