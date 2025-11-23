"""Category CRUD Handler with pattern management and cache invalidation."""

from pathlib import Path
from typing import Any, Dict, List

from ..exceptions import SecurityError
from ..handlers.unified_crud_handler import UnifiedCrudHandler
from ..models.enhanced_instruction import EnhancedInstruction
from ..security.path_validator import PathValidator


class CategoryCrudHandler(UnifiedCrudHandler):
    """CRUD handler for category operations with pattern management."""

    def _handle_add(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle add category operation."""
        if not instruction.name:
            return {"success": False, "error": "Category name is required"}

        # Validate category name (basic sanitization)
        if not instruction.name.replace("_", "").replace("-", "").isalnum():
            return {
                "success": False,
                "error": "Category name must contain only alphanumeric characters, hyphens, and underscores",
            }

        # Validate required fields
        if not hasattr(instruction, "dir") or not instruction.dir:
            return {"success": False, "error": "Category directory is required"}

        # Validate directory path
        try:
            validator = PathValidator([Path.cwd()])
            validator.validate_path(instruction.dir, Path.cwd())
        except SecurityError as e:
            return {"success": False, "error": f"Invalid directory path: {e}"}

        if not hasattr(instruction, "patterns") or not instruction.patterns:
            return {"success": False, "error": "Category patterns are required"}

        # Create category data
        category_data = {"name": instruction.name, "dir": instruction.dir, "patterns": instruction.patterns}

        # Add optional description
        if hasattr(instruction, "description") and instruction.description:
            category_data["description"] = instruction.description

        # Invalidate cache after successful add
        self._invalidate_category_cache(instruction.name)

        return {
            "success": True,
            "action": "add",
            "category": category_data,
            "message": f"Category '{instruction.name}' added successfully",
        }

    def _handle_update(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle update category operation."""
        if not instruction.name:
            return {"success": False, "error": "Category name is required"}

        update_data: Dict[str, Any] = {"name": instruction.name}

        # Update directory if provided
        if hasattr(instruction, "dir") and instruction.dir:
            update_data["dir"] = instruction.dir

        # Update patterns if provided
        if hasattr(instruction, "patterns") and instruction.patterns:
            if not self._validate_patterns(instruction.patterns):
                return {"success": False, "error": "Invalid patterns format"}
            update_data["patterns"] = instruction.patterns

        # Update description if provided
        if hasattr(instruction, "description"):
            update_data["description"] = instruction.description or ""

        # Invalidate cache after successful update
        self._invalidate_category_cache(instruction.name)

        return {
            "success": True,
            "action": "update",
            "category": update_data,
            "message": f"Category '{instruction.name}' updated successfully",
        }

    def _handle_remove(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle remove category operation."""
        if not instruction.name:
            return {"success": False, "error": "Category name is required"}

        # Invalidate cache before removal
        self._invalidate_category_cache(instruction.name)

        return {
            "success": True,
            "action": "remove",
            "category": instruction.name,
            "message": f"Category '{instruction.name}' removed successfully",
        }

    def _handle_delete(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle delete category operation (alias for remove)."""
        return self._handle_remove(instruction)

    def _handle_list(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle list categories operation."""
        # Return mock data for now - would integrate with actual category storage
        categories = [
            {"name": "docs", "dir": "./docs", "patterns": ["*.md", "*.txt"]},
            {"name": "code", "dir": "./src", "patterns": ["*.py", "*.js"]},
        ]

        return {"success": True, "action": "list", "categories": categories, "count": len(categories)}

    def _handle_append(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle append patterns to category operation."""
        if not instruction.name:
            return {"success": False, "error": "Category name is required"}

        if not hasattr(instruction, "patterns") or not instruction.patterns:
            return {"success": False, "error": "Patterns to append are required"}

        if not self._validate_patterns(instruction.patterns):
            return {"success": False, "error": "Invalid patterns format"}

        # Invalidate cache after successful append
        self._invalidate_category_cache(instruction.name)

        return {
            "success": True,
            "action": "append",
            "category": instruction.name,
            "patterns": instruction.patterns,
            "message": f"Patterns appended to category '{instruction.name}' successfully",
        }

    def _validate_patterns(self, patterns: List[str]) -> bool:
        """Validate category patterns format."""
        if not isinstance(patterns, list):
            return False

        for pattern in patterns:
            if not isinstance(pattern, str) or len(pattern.strip()) == 0:
                return False

        return True

    def _invalidate_category_cache(self, category_name: str) -> None:
        """Invalidate cache for the specified category."""
        if hasattr(self.session_manager, "invalidate_cache"):
            self.session_manager.invalidate_cache(f"category:{category_name}")

    def _invalidate_all_category_cache(self) -> None:
        """Invalidate all category-related cache."""
        if hasattr(self.session_manager, "invalidate_cache"):
            self.session_manager.invalidate_cache("category:*")
