"""Base operation class for generic CRUD operations."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any
from pydantic import BaseModel, ValidationError

from ..models.project_config import ProjectConfig

T = TypeVar("T")


class BaseOperation(BaseModel, Generic[T], ABC):
    """Abstract base class for all operations."""

    @abstractmethod
    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Execute the operation and return result."""
        pass

    def _success_response(self, **kwargs: Any) -> Dict[str, Any]:
        """Create a success response."""
        return {"success": True, **kwargs}

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Create an error response."""
        return {"success": False, "error": error}


async def execute_json_operation(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Generic JSON operation executor."""
    from ..session_manager import SessionManager
    from .registry import get_operation_class

    try:
        action = data.get("action")
        if not action:
            return {"success": False, "error": "No action specified"}

        operation_class = get_operation_class(entity_type, action)
        operation = operation_class.model_validate(data)

        session_manager = SessionManager()
        project = session_manager.get_project_name()
        config = await session_manager.get_or_create_project_config(project)

        return await operation.execute(config)

    except ValueError as e:
        return {"success": False, "error": str(e)}
    except ValidationError as e:
        return {"success": False, "error": f"Validation failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
