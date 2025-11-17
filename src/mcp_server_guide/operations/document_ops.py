"""Document-specific operations."""

from typing import Dict, Any, Optional
from .operation_base import BaseOperation
from ..tools.document_tools import create_mcp_document, update_mcp_document, delete_mcp_document, list_mcp_documents
from ..models.project_config import ProjectConfig


class DocumentCreateOperation(BaseOperation):
    """Create a new document."""

    name: str
    category_dir: str
    content: str
    mime_type: Optional[str] = None
    source_type: str = "manual"

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await create_mcp_document(
            category_dir=self.category_dir,
            name=self.name,
            content=self.content,
            explicit_action="CREATE_DOCUMENT",
            mime_type=self.mime_type,
            source_type=self.source_type,
        )


class DocumentUpdateOperation(BaseOperation):
    """Update an existing document."""

    name: str
    category_dir: str
    content: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await update_mcp_document(
            category_dir=self.category_dir, name=self.name, content=self.content, explicit_action="UPDATE_DOCUMENT"
        )


class DocumentDeleteOperation(BaseOperation):
    """Delete a document."""

    name: str
    category_dir: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await delete_mcp_document(
            category_dir=self.category_dir, name=self.name, explicit_action="DELETE_DOCUMENT"
        )


class DocumentListOperation(BaseOperation):
    """List documents."""

    category_dir: str
    mime_type: Optional[str] = None
    source_type: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await list_mcp_documents(
            category_dir=self.category_dir, mime_type=self.mime_type, source_type=self.source_type
        )
