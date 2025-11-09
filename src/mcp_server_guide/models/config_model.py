"""Config model with operation mappings."""

from types import MappingProxyType
from typing import Dict, Any, Optional, ClassVar, Type
from ..operations.model_base import BaseModelOperations
from ..operations.operation_base import BaseOperation


class ConfigModel(BaseModelOperations):
    """Model representing config with its operations."""

    operations: ClassVar[Dict[str, Type[BaseOperation]]] = {}

    @classmethod
    def get_operations(cls) -> MappingProxyType[str, Type[BaseOperation]]:
        """Get the operations mapping for this model."""
        if not cls.operations:
            # Local imports to avoid circular dependency
            from ..operations.config_ops import (
                GetCurrentProjectOperation,
                GetProjectConfigOperation,
                SetProjectConfigOperation,
                SetProjectConfigValuesOperation,
                SwitchProjectOperation,
            )

            cls.operations = {
                "get_current_project": GetCurrentProjectOperation,
                "get_project_config": GetProjectConfigOperation,
                "set_project_config": SetProjectConfigOperation,
                "set_project_config_values": SetProjectConfigValuesOperation,
                "switch_project": SwitchProjectOperation,
            }
        return MappingProxyType(cls.operations)

    project: Optional[str] = None
    config_key: Optional[str] = None
    value: Optional[Any] = None
    config_dict: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
