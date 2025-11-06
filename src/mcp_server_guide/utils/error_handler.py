"""Shared error handling utilities for consistent error responses."""

from typing import Dict, Any, Optional
from ..logging_config import get_logger

logger = get_logger()

def handle_operation_error(operation_name: str, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Standard error handling for all operations.

    Args:
        operation_name: Name of the operation that failed
        error: The exception that occurred
        context: Optional context information for logging

    Returns:
        Standardized error response dictionary
    """
    context_str = f" (context: {context})" if context else ""

    if isinstance(error, FileNotFoundError):
        logger.warning(f"{operation_name} failed - file not found: {error}{context_str}")
        return {"success": False, "error": f"File not found: {str(error)}", "error_type": "not_found"}
    elif isinstance(error, PermissionError):
        logger.warning(f"{operation_name} failed - permission denied: {error}{context_str}")
        return {"success": False, "error": f"Permission denied: {str(error)}", "error_type": "permission"}
    elif isinstance(error, OSError):
        logger.warning(f"{operation_name} failed - filesystem error: {error}{context_str}")
        return {"success": False, "error": f"File system error: {str(error)}", "error_type": "filesystem"}
    elif isinstance(error, UnicodeDecodeError):
        logger.warning(f"{operation_name} failed - encoding error: {error}{context_str}")
        return {"success": False, "error": f"Encoding error: {str(error)}", "error_type": "encoding"}
    else:
        logger.exception(f"Unexpected error in {operation_name}{context_str}")
        return {"success": False, "error": f"Unexpected error: {str(error)}", "error_type": "unexpected"}
