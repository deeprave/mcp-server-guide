"""Enhanced instruction model with flexible action placement and field validation."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class EnhancedInstruction(BaseModel):
    """Enhanced instruction model supporting flexible action placement and validation."""

    # Core fields
    action: str = Field(..., description="Action to perform")
    name: Optional[str] = Field(None, description="Name of the entity")

    # Category fields
    dir: Optional[str] = Field(None, description="Directory path for category")
    patterns: Optional[List[str]] = Field(None, description="File patterns for category")

    # Collection fields
    categories: Optional[List[str]] = Field(None, description="Categories in collection")

    # Document fields
    category: Optional[str] = Field(None, description="Category for document")
    data: Optional[List[str]] = Field(None, description="Document content data array")

    # Common fields
    description: Optional[str] = Field(None, description="Description of the entity")

    # List operation fields
    entity: Optional[str] = Field(None, description="Entity type for list operations")
    verbose: Optional[bool] = Field(None, description="Verbose output for list operations")

    # Flexible args field for action extraction
    args: Optional[Dict[str, Any]] = Field(None, description="Additional arguments")

    @model_validator(mode="before")
    @classmethod
    def extract_action(cls, data: Any) -> Any:
        """Extract action from root level or args level."""
        if isinstance(data, dict):
            # Check if action is at root level
            if "action" in data:
                return data

            # Check if action is in args
            if "args" in data and isinstance(data["args"], dict) and "action" in data["args"]:
                # Move action from args to root level
                data = data.copy()
                data["action"] = data["args"]["action"]
                return data

            # Check if action is at the same level as other fields (extracted automatically)
            # This handles the case where action is mixed with other fields
            action_keys = {"action"}
            if action_keys.intersection(data.keys()):
                return data

        return data

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate that action is one of the allowed values."""
        valid_actions = {"add", "delete", "update", "append", "remove", "list"}
        if v not in valid_actions:
            raise ValueError(f"Invalid action '{v}'. Must be one of: {', '.join(sorted(valid_actions))}")
        return v

    @model_validator(mode="after")
    def validate_required_action(self) -> "EnhancedInstruction":
        """Ensure action is present after all processing."""
        if not self.action:
            raise ValueError("Action is required")
        return self
