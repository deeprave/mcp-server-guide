"""Base operation class without circular dependencies."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel


class BaseOperation(BaseModel, ABC):
    """Abstract base class for all operations."""

    @abstractmethod
    async def execute(self, config: Any) -> Dict[str, Any]:
        """Execute the operation with the given configuration."""
        pass

    def _success_response(self, **kwargs: Any) -> Dict[str, Any]:
        """Create a success response."""
        return {"success": True, **kwargs}

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Create an error response."""
        return {"success": False, "error": error}
