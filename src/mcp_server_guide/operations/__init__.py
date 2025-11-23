"""Simplified operation framework for type-safe JSON instruction handling."""

from .base import execute_json_operation
from .model_base import BaseModelOperations, discover_models
from .operation_base import BaseOperation
from .schema_generator import generate_tool_description

__all__ = [
    "BaseModelOperations",
    "BaseOperation",
    "execute_json_operation",
    "discover_models",
    "generate_tool_description",
]
