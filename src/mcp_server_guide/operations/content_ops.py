"""Content-specific operations."""

from typing import Dict, Any, Optional
from .operation_base import BaseOperation
from ..tools.content_tools import get_content, search_content
from ..tools.file_tools import get_file_content
from ..models.project_config import ProjectConfig


class GetContentOperation(BaseOperation):
    """Get content by category or collection."""

    category_or_collection: str
    document: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        content = await get_content(category_or_collection=self.category_or_collection, document=self.document)
        return {"success": True, "content": content}


class SearchContentOperation(BaseOperation):
    """Search content."""

    query: str
    project: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        results = await search_content(query=self.query, project=self.project)
        return {"success": True, "results": results}


class GetFileContentOperation(BaseOperation):
    """Get file content."""

    path: str
    project: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        content = await get_file_content(path=self.path, project=self.project)
        return {"success": True, "content": content}
