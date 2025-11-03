"""Spec instruction model for structured client instructions."""

from typing import List, Dict, Any
import json
from pydantic import BaseModel


class SpecInstruction(BaseModel):
    """Represents a single instruction for client-side operations."""

    action: str
    description: str
    # Additional fields can be added when actually needed

    def to_dict(self) -> Dict[str, Any]:
        """Convert instruction to dictionary format."""
        return {"action": self.action, "description": self.description}


class SpecInstructionSet(BaseModel):
    """Represents a complete set of instructions with summary."""

    instructions: List[SpecInstruction]
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert instruction set to dictionary format."""
        return {"instructions": [inst.to_dict() for inst in self.instructions], "summary": self.summary}

    def to_json(self) -> str:
        """Convert instruction set to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
