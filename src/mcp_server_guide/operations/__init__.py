"""Simplified operation framework for type-safe JSON instruction handling."""

from .model_base import BaseModelOperations, discover_models
from .operation_base import BaseOperation
from .base import execute_json_operation
from .schema_generator import generate_tool_description

__all__ = [
    "BaseModelOperations",
    "BaseOperation",
    "execute_json_operation",
    "discover_models",
    "generate_tool_description",
]
