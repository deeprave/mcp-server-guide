"""Base class for models that define operations."""

from types import MappingProxyType
from typing import Dict, Type, ClassVar
from pydantic import BaseModel

from .operation_base import BaseOperation


class BaseModelOperations(BaseModel):
    """Base class for models that define their own operations."""

    operations: ClassVar[Dict[str, Type[BaseOperation]]] = {}

    @classmethod
    def get_operations(cls) -> MappingProxyType[str, Type[BaseOperation]]:
        """Get the operations mapping for this model."""
        return MappingProxyType(cls.operations)

    @classmethod
    def get_operation_class(cls, action: str) -> Type["BaseOperation"]:
        """Get operation class for the given action."""
        operations = cls.get_operations()
        if action not in operations:
            raise ValueError(f"Unknown action '{action}' for {cls.__name__}")

        return operations[action]  # type: ignore[return-value]


_discovered_models: list[Type[BaseModelOperations]] | None = None

def discover_models() -> list[Type[BaseModelOperations]]:
    """Discover all model classes that define operations."""
    global _discovered_models
    if _discovered_models is not None:
        return _discovered_models

    import importlib
    import pkgutil
    from .. import models

    # Dynamically import all modules in the models package
    for _, module_name, _ in pkgutil.iter_modules(models.__path__, f"{models.__name__}."):
        if module_name.endswith("_model"):  # Only import *_model modules
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                # Log specific import issues for debugging
                import logging
                logging.getLogger(__name__).warning(f"Failed to import {module_name}: {e}")

    _discovered_models = BaseModelOperations.__subclasses__()
    return _discovered_models
