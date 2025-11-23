"""Input validation framework for MCP server guide."""

import re
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from .exceptions import ValidationError

# ============================================================================
# Input Validation Framework
# ============================================================================


class ValidationRule:
    """A single validation rule with validator function and error message."""

    def __init__(self, validator: Callable[[Any], bool], error_message: str):
        self.validator = validator
        self.error_message = error_message

    def validate(self, value: Any) -> None:
        """Validate a value against this rule.

        Args:
            value: Value to validate

        Raises:
            ValidationError: If validation fails
        """
        if not self.validator(value):
            raise ValidationError(self.error_message)


class InputValidator:
    """Validates input data against defined rules."""

    def __init__(self) -> None:
        self.rules: Dict[str, List[ValidationRule]] = {}

    def add_rule(self, field: str, rule: ValidationRule) -> None:
        """Add a validation rule for a field.

        Args:
            field: Field name to validate
            rule: Validation rule to apply
        """
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append(rule)

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate data against all defined rules.

        Args:
            data: Data dictionary to validate

        Raises:
            ValidationError: If any validation fails
        """
        for field, value in data.items():
            if field in self.rules:
                for rule in self.rules[field]:
                    try:
                        rule.validate(value)
                    except ValidationError as e:
                        # Add field context to error
                        raise ValidationError(
                            f"Validation failed for field '{field}': {e}",
                            context={"field": field, "value": str(value)[:100]},
                        ) from e


def validate_input(**field_rules: Union[ValidationRule, List[ValidationRule]]) -> Callable[..., Any]:
    """Decorator to validate function inputs.

    Args:
        **field_rules: Mapping of field names to ValidationRule objects or lists

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            validator = InputValidator()
            for field, rules in field_rules.items():
                if not isinstance(rules, list):
                    rules = [rules]
                for rule in rules:
                    validator.add_rule(field, rule)

            # Validate kwargs
            validator.validate(kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Pre-built validation rules
class ValidationRules:
    """Collection of common validation rules."""

    @staticmethod
    def non_empty_string() -> ValidationRule:
        """Validate that value is a non-empty string."""
        return ValidationRule(lambda x: isinstance(x, str) and len(x.strip()) > 0, "Value must be a non-empty string")

    @staticmethod
    def max_length(max_len: int) -> ValidationRule:
        """Validate that string length doesn't exceed maximum."""
        return ValidationRule(
            lambda x: isinstance(x, str) and len(x) <= max_len, f"Value exceeds maximum length of {max_len} characters"
        )

    @staticmethod
    def min_length(min_len: int) -> ValidationRule:
        """Validate that string length meets minimum."""
        return ValidationRule(
            lambda x: isinstance(x, str) and len(x) >= min_len, f"Value must be at least {min_len} characters long"
        )

    @staticmethod
    def valid_url() -> ValidationRule:
        """Validate that value is a valid HTTP/HTTPS URL."""
        return ValidationRule(
            lambda x: isinstance(x, str) and x.startswith(("http://", "https://")),
            "Value must be a valid HTTP/HTTPS URL",
        )

    @staticmethod
    def safe_filename() -> ValidationRule:
        """Validate that filename contains no unsafe characters."""
        return ValidationRule(
            lambda x: isinstance(x, str)
            and not any(c in x for c in ["..", "/", "\\", ":", "*", "?", '"', "<", ">", "|"]),
            "Filename contains unsafe characters",
        )

    @staticmethod
    def safe_path() -> ValidationRule:
        """Validate that path contains no traversal sequences."""
        return ValidationRule(
            lambda x: isinstance(x, str) and ".." not in x and not x.startswith("/"),
            "Path contains unsafe traversal sequences or absolute path",
        )

    @staticmethod
    def alphanumeric() -> ValidationRule:
        """Validate that value contains only alphanumeric characters."""
        return ValidationRule(
            lambda x: isinstance(x, str) and x.isalnum(), "Value must contain only alphanumeric characters"
        )

    @staticmethod
    def regex_pattern(pattern: str, message: Optional[str] = None) -> ValidationRule:
        """Validate that value matches regex pattern."""
        compiled_pattern = re.compile(pattern)
        default_message = f"Value must match pattern: {pattern}"
        return ValidationRule(
            lambda x: isinstance(x, str) and compiled_pattern.match(x) is not None, message or default_message
        )

    @staticmethod
    def one_of(allowed_values: List[Any]) -> ValidationRule:
        """Validate that value is one of allowed values."""
        return ValidationRule(
            lambda x: x in allowed_values, f"Value must be one of: {', '.join(str(v) for v in allowed_values)}"
        )

    @staticmethod
    def integer_range(min_val: Optional[int] = None, max_val: Optional[int] = None) -> ValidationRule:
        """Validate that value is an integer within range."""

        def validator(x: Any) -> bool:
            if not isinstance(x, int):
                return False
            if min_val is not None and x < min_val:
                return False
            if max_val is not None and x > max_val:
                return False
            return True

        range_desc = []
        if min_val is not None:
            range_desc.append(f"minimum {min_val}")
        if max_val is not None:
            range_desc.append(f"maximum {max_val}")

        message = "Value must be an integer"
        if range_desc:
            message += f" with {' and '.join(range_desc)}"

        return ValidationRule(validator, message)

    @staticmethod
    def email() -> ValidationRule:
        """Validate that value is a valid email address."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return ValidationRule(
            lambda x: isinstance(x, str) and re.match(email_pattern, x) is not None,
            "Value must be a valid email address",
        )


# Convenience aliases for common rules
RULES = ValidationRules
