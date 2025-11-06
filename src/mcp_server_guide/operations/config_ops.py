"""Config-specific operations."""

from typing import Dict, Any, Optional
from .operation_base import BaseOperation
from ..tools.config_tools import get_project_config, set_project_config, set_project_config_values
from ..tools.project_tools import get_current_project, switch_project
from ..models.project_config import ProjectConfig


class GetCurrentProjectOperation(BaseOperation):
    """Get current project."""

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        project = await get_current_project()
        return {"success": True, "project": project}


class GetProjectConfigOperation(BaseOperation):
    """Get project config."""

    project: Optional[str] = None

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await get_project_config(project=self.project)


class SetProjectConfigOperation(BaseOperation):
    """Set project config."""

    config_key: str
    value: Any

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await set_project_config(config_key=self.config_key, value=self.value)


class SetProjectConfigValuesOperation(BaseOperation):
    """Set multiple project config values."""

    config_dict: Dict[str, Any]

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await set_project_config_values(config_dict=self.config_dict)


class SwitchProjectOperation(BaseOperation):
    """Switch project."""

    name: str

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        return await switch_project(name=self.name)
