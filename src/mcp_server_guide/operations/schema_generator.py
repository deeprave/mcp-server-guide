"""Schema generation for operation tool descriptions."""

import json
from typing import Any, Dict
from .registry import OPERATION_REGISTRY, get_operation_schema


def generate_tool_description(entity_type: str) -> str:
    """Generate dynamic tool description from Pydantic schemas."""
    entity_ops = OPERATION_REGISTRY.get(entity_type)
    if not entity_ops:
        return f"Handle {entity_type} operations via JSON instructions."

    schema_lines = [f"SCHEMA - Valid actions and arguments for {entity_type}:"]

    for action, operation_class in entity_ops.items():
        schema = operation_class.model_json_schema()
        required_fields = schema.get("required", [])
        required_fields = [f for f in required_fields if f != "action"]

        if required_fields:
            schema_lines.append(f"- {action}: {', '.join(required_fields)}")
        else:
            schema_lines.append(f"- {action}: (no additional fields)")

    # Generate example using first action
    first_action = next(iter(entity_ops.keys()))
    example_schema = get_operation_schema(entity_type, first_action)

    example_data: Dict[str, Any] = {"action": first_action}
    properties = example_schema.get("properties", {})
    required = example_schema.get("required", [])

    for field in required:
        if field != "action" and field in properties:
            prop = properties[field]
            if prop.get("type") == "string":
                example_data[field] = "example_value"
            elif prop.get("type") == "array":
                example_data[field] = ["item1", "item2"]
            elif prop.get("type") == "boolean":
                example_data[field] = True
            else:
                example_data[field] = "value"

    example_json = json.dumps(example_data, indent=2)

    return f"""Handle {entity_type} operations via JSON instructions.

{chr(10).join(schema_lines)}

Example JSON:
{example_json}"""
