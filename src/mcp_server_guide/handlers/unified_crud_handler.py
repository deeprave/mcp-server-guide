"""Unified CRUD Handler with common validation and routing."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..models.enhanced_instruction import EnhancedInstruction
from ..utils.text_conversion import decode_data_array, encode_data_array


class UnifiedCrudHandler(ABC):
    """Base class for all CRUD handlers with common validation and routing."""

    def __init__(self, session_manager: Any) -> None:
        """Initialize with session manager for state access."""
        self.session_manager = session_manager

    def handle_instruction(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Route instruction to appropriate handler method based on action."""
        action = instruction.action

        if action == "add":
            return self._handle_add(instruction)
        elif action == "update":
            return self._handle_update(instruction)
        elif action == "remove":
            return self._handle_remove(instruction)
        elif action == "delete":
            return self._handle_delete(instruction)
        elif action == "list":
            return self._handle_list(instruction)
        elif action == "append":
            return self._handle_append(instruction)
        else:
            return {"success": False, "error": f"Unsupported action: {action}"}

    def _process_data_array(self, instruction: EnhancedInstruction) -> Optional[list]:
        """Process data array if present in instruction."""
        if hasattr(instruction, "data") and instruction.data:
            try:
                return decode_data_array(instruction.data)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid data array: {e}")
        return None

    def _encode_response_data(self, data: list) -> list:
        """Encode response data array for output."""
        try:
            return encode_data_array(data)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to encode response data: {e}")

    @abstractmethod
    def _handle_add(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle add operation."""
        pass

    @abstractmethod
    def _handle_update(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle update operation."""
        pass

    @abstractmethod
    def _handle_remove(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle remove operation."""
        pass

    @abstractmethod
    def _handle_delete(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle delete operation."""
        pass

    @abstractmethod
    def _handle_list(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle list operation."""
        pass

    @abstractmethod
    def _handle_append(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle append operation."""
        pass
