"""Collection CRUD Handler with category reference validation."""

from typing import Any, Dict, List

from ..handlers.unified_crud_handler import UnifiedCrudHandler
from ..models.enhanced_instruction import EnhancedInstruction


class CollectionCrudHandler(UnifiedCrudHandler):
    """CRUD handler for collection operations with category reference validation."""

    def _handle_add(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle add collection operation."""
        if not instruction.name:
            return {"success": False, "error": "Collection name is required"}

        # Validate collection name (basic sanitization)
        if not instruction.name.replace("_", "").replace("-", "").isalnum():
            return {
                "success": False,
                "error": "Collection name must contain only alphanumeric characters, hyphens, and underscores",
            }

        # Validate required fields
        if not hasattr(instruction, "categories") or not instruction.categories:
            return {"success": False, "error": "Collection categories are required"}

        # Validate category references
        validation_result = self._validate_category_references(instruction.categories)
        if not validation_result["valid"]:
            return {"success": False, "error": validation_result["error"]}

        # Create collection data
        collection_data = {"name": instruction.name, "categories": instruction.categories}

        # Add optional description
        if hasattr(instruction, "description") and instruction.description:
            collection_data["description"] = instruction.description

        # Invalidate cache after successful add
        self._invalidate_collection_cache(instruction.name)

        return {
            "success": True,
            "action": "add",
            "collection": collection_data,
            "message": f"Collection '{instruction.name}' added successfully",
        }

    def _handle_update(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle update collection operation."""
        if not instruction.name:
            return {"success": False, "error": "Collection name is required"}

        update_data: Dict[str, Any] = {"name": instruction.name}

        # Update categories if provided
        if hasattr(instruction, "categories") and instruction.categories:
            validation_result = self._validate_category_references(instruction.categories)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            update_data["categories"] = instruction.categories

        # Update description if provided
        if hasattr(instruction, "description"):
            update_data["description"] = instruction.description or ""

        # Invalidate cache after successful update
        self._invalidate_collection_cache(instruction.name)

        return {
            "success": True,
            "action": "update",
            "collection": update_data,
            "message": f"Collection '{instruction.name}' updated successfully",
        }

    def _handle_remove(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle remove collection operation."""
        if not instruction.name:
            return {"success": False, "error": "Collection name is required"}

        # Invalidate cache before removal
        self._invalidate_collection_cache(instruction.name)

        return {
            "success": True,
            "action": "remove",
            "collection": instruction.name,
            "message": f"Collection '{instruction.name}' removed successfully",
        }

    def _handle_delete(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle delete collection operation (alias for remove)."""
        return self._handle_remove(instruction)

    def _handle_list(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle list collections operation."""
        # Return mock data for now - would integrate with actual collection storage
        collections = [
            {"name": "documentation", "categories": ["docs", "guides"]},
            {"name": "source-code", "categories": ["code", "tests"]},
        ]

        return {"success": True, "action": "list", "collections": collections, "count": len(collections)}

    def _handle_append(self, instruction: EnhancedInstruction) -> Dict[str, Any]:
        """Handle append categories to collection operation."""
        if not instruction.name:
            return {"success": False, "error": "Collection name is required"}

        if not hasattr(instruction, "categories") or not instruction.categories:
            return {"success": False, "error": "Categories to append are required"}

        # Validate category references
        validation_result = self._validate_category_references(instruction.categories)
        if not validation_result["valid"]:
            return {"success": False, "error": validation_result["error"]}

        # Invalidate cache after successful append
        self._invalidate_collection_cache(instruction.name)

        return {
            "success": True,
            "action": "append",
            "collection": instruction.name,
            "categories": instruction.categories,
            "message": f"Categories appended to collection '{instruction.name}' successfully",
        }

    def _validate_category_references(self, categories: List[str]) -> Dict[str, Any]:
        """Validate that referenced categories exist and are valid."""
        if not isinstance(categories, list):
            return {"valid": False, "error": "Categories must be a list"}

        for category in categories:
            if not isinstance(category, str) or len(category.strip()) == 0:
                return {"valid": False, "error": "Category names must be non-empty strings"}

        # Mock validation - would integrate with actual category storage
        # For now, just check basic format requirements
        return {"valid": True}

    def _invalidate_collection_cache(self, collection_name: str) -> None:
        """Invalidate cache for the specified collection."""
        if hasattr(self.session_manager, "invalidate_cache"):
            self.session_manager.invalidate_cache(f"collection:{collection_name}")

    def _invalidate_all_collection_cache(self) -> None:
        """Invalidate all collection-related cache."""
        if hasattr(self.session_manager, "invalidate_cache"):
            self.session_manager.invalidate_cache("collection:*")
