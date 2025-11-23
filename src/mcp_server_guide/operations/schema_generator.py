"""Schema generation for operation tool descriptions."""

import json
from typing import Any, Dict, List, Type

from .model_base import BaseModelOperations, discover_models


def _extract_schema_info(operations: Dict[str, Type[Any]], model_class: Type[BaseModelOperations]) -> List[str]:
    """Extract schema information for actions."""
    schema_lines = []
    for action, operation_class in operations.items():
        try:
            schema = operation_class.model_json_schema()
            required_fields = [f for f in schema.get("required", []) if f != "action"]

            if required_fields:
                schema_lines.append(f"- {action}: {', '.join(required_fields)}")
            else:
                schema_lines.append(f"- {action}: (no additional fields)")
        except (AttributeError, ValueError, KeyError) as e:
            # Handle specific schema-related errors consistently
            schema_lines.append(f"- {action}: (schema unavailable: {type(e).__name__})")
        except Exception:
            # Handle unexpected errors - match test expectation
            schema_lines.append(f"- {action}: (schema unavailable)")
    return schema_lines


def _generate_example_data(entity_type: str, model_class: Type[BaseModelOperations]) -> str:
    """Generate example JSON for the first action."""
    operations = model_class.get_operations()
    if not operations:
        return json.dumps({"action": "example"}, indent=2)

    first_action = next(iter(operations.keys()))
    first_operation_class = operations[first_action]

    try:
        schema = first_operation_class.model_json_schema()

        example_data: Dict[str, Any] = {"action": first_action}
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for field in required:
            if field != "action" and field in properties:
                prop = properties[field]
                prop_type = prop.get("type")
                if prop_type == "string":
                    example_data[field] = f"example_{field}"
                elif prop_type == "array":
                    example_data[field] = ["item1", "item2"]
                elif prop_type == "boolean":
                    example_data[field] = True
                else:
                    example_data[field] = "value"

        return json.dumps(example_data, indent=2)
    except (AttributeError, ValueError, KeyError) as e:
        # Handle specific schema-related errors consistently
        return json.dumps({"action": first_action, "error": f"schema_error_{type(e).__name__}"}, indent=2)
    except Exception:
        # Handle unexpected errors
        return json.dumps({"action": first_action}, indent=2)


def generate_tool_description(entity_type: str) -> str:
    """Generate dynamic tool description from Pydantic schemas."""
    # Find model class by entity_type
    model_class = None
    for cls in discover_models():
        if cls.__name__.lower().replace("model", "") == entity_type:
            model_class = cls
            break

    if not model_class:
        return f"Handle {entity_type} operations via JSON instructions."

    operations = model_class.get_operations()
    if not operations:
        return f"Handle {entity_type} operations via JSON instructions."

    schema_lines = [f"SCHEMA - Valid actions and arguments for {entity_type}:"]
    schema_lines.extend(_extract_schema_info(dict(operations), model_class))
    example_json = _generate_example_data(entity_type, model_class)

    return f"""Handle {entity_type} operations via JSON instructions.

{chr(10).join(schema_lines)}

EXAMPLE:
{example_json}"""


def get_all_schemas() -> Dict[str, Any]:
    """Get schemas for all contexts."""
    schemas: Dict[str, Any] = {}
    model_classes = discover_models()

    for model_class in model_classes:
        entity_type = model_class.__name__.lower().replace("model", "")
        operations = model_class.get_operations()

        context_schema: Dict[str, Any] = {"entity_type": entity_type, "actions": {}}

        for action, operation_class in operations.items():
            try:
                schema = operation_class.model_json_schema()
                context_schema["actions"][action] = {
                    "required": [f for f in schema.get("required", []) if f != "action"],
                    "properties": {k: v for k, v in schema.get("properties", {}).items() if k != "action"},
                }
            except Exception:
                context_schema["actions"][action] = {"error": "schema unavailable"}

        schemas[entity_type] = context_schema

    return schemas


def get_schema_for_context(context: str) -> Dict[str, Any]:
    """Get schema for specific context."""
    all_schemas = get_all_schemas()
    return all_schemas.get(context, {})  # type: ignore[no-any-return]
