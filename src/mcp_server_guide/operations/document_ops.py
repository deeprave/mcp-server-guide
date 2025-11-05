"""Document-specific operations."""

from typing import Dict, Any, Optional
from .crud import AddOperation, UpdateOperation, RemoveOperation, ListOperation
from ..tools.document_tools import create_mcp_document, update_mcp_document, delete_mcp_document, list_mcp_documents
from ..models.project_config import ProjectConfig


class DocumentCreateOperation(AddOperation):
    """Create a new document."""

    category_dir: str
    content: str
    mime_type: Optional[str] = None
    source_type: str = "manual"

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await create_mcp_document(
            category_dir=self.category_dir,
            name=self.name,
            content=self.content,
            mime_type=self.mime_type,
            source_type=self.source_type,
        )


class DocumentUpdateOperation(UpdateOperation):
    """Update an existing document."""

    category_dir: str
    content: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await update_mcp_document(category_dir=self.category_dir, name=self.name, content=self.content)


class DocumentDeleteOperation(RemoveOperation):
    """Delete a document."""

    category_dir: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await delete_mcp_document(category_dir=self.category_dir, name=self.name)


class DocumentListOperation(ListOperation):
    """List documents."""

    category_dir: str
    mime_type: Optional[str] = None
    source_type: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await list_mcp_documents(
            category_dir=self.category_dir, mime_type=self.mime_type, source_type=self.source_type
        )
