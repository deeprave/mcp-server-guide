"""Base operation classes for simplified architecture."""

from typing import Dict, Any
from pydantic import ValidationError

from .model_base import discover_models


async def execute_json_operation(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Generic JSON operation executor."""
    from ..session_manager import SessionManager

    try:
        action = data.get("action")
        if not action:
            return {"success": False, "error": "No action specified"}

        model_class = next(
            (cls for cls in discover_models() if cls.__name__.lower().replace("model", "") == entity_type),
            None,
        )
        if not model_class:
            return {"success": False, "error": f"Unknown entity type: {entity_type}"}

        operation_class = model_class.get_operation_class(action)
        operation = operation_class.model_validate(data)

        session_manager = SessionManager()
        project = session_manager.get_project_name()
        config = await session_manager.get_or_create_project_config(project)

        return await operation.execute(config)  # type: ignore[no-any-return]

    except ValidationError as e:
        return {"success": False, "error": f"Validation failed: {str(e)}"}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except (AttributeError, KeyError) as e:
        from ..logging_config import get_logger
        logger = get_logger()
        logger.error(f"Configuration error in execute_json_operation: {e}", exc_info=True)
        return {"success": False, "error": "Configuration error - check server setup"}
    except Exception as e:
        from ..logging_config import get_logger
        logger = get_logger()
        logger.exception(f"Unexpected error in execute_json_operation: {e}")
        return {"success": False, "error": f"Operation failed: {str(e)}"}
