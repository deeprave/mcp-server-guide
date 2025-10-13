"""Tests for input validation framework."""

import pytest
from mcp_server_guide.validation import ValidationRule, InputValidator, validate_input, ValidationRules, RULES
from mcp_server_guide.exceptions import ValidationError


class TestValidationRule:
    """Test ValidationRule functionality."""

    def test_validation_rule_success(self):
        """Test successful validation."""
        rule = ValidationRule(lambda x: x > 0, "Value must be positive")

        # Should not raise exception
        rule.validate(5)
        rule.validate(1)

    def test_validation_rule_failure(self):
        """Test failed validation."""
        rule = ValidationRule(lambda x: x > 0, "Value must be positive")

        with pytest.raises(ValidationError, match="Value must be positive"):
            rule.validate(-1)

        with pytest.raises(ValidationError, match="Value must be positive"):
            rule.validate(0)


class TestInputValidator:
    """Test InputValidator functionality."""

    def test_validator_with_single_rule(self):
        """Test validator with single rule."""
        validator = InputValidator()
        rule = ValidationRule(lambda x: isinstance(x, str), "Must be string")
        validator.add_rule("name", rule)

        # Valid data should pass
        validator.validate({"name": "John"})

        # Invalid data should fail
        with pytest.raises(ValidationError, match="Validation failed for field 'name'"):
            validator.validate({"name": 123})

    def test_validator_with_multiple_rules(self):
        """Test validator with multiple rules for same field."""
        validator = InputValidator()
        validator.add_rule("password", ValidationRule(lambda x: isinstance(x, str), "Must be string"))
        validator.add_rule("password", ValidationRule(lambda x: len(x) >= 8, "Must be at least 8 characters"))

        # Valid data should pass
        validator.validate({"password": "password123"})

        # Invalid data should fail on first rule
        with pytest.raises(ValidationError, match="Must be string"):
            validator.validate({"password": 123})

        # Invalid data should fail on second rule
        with pytest.raises(ValidationError, match="Must be at least 8 characters"):
            validator.validate({"password": "short"})

    def test_validator_with_multiple_fields(self):
        """Test validator with multiple fields."""
        validator = InputValidator()
        validator.add_rule("name", ValidationRule(lambda x: isinstance(x, str), "Name must be string"))
        validator.add_rule(
            "age", ValidationRule(lambda x: isinstance(x, int) and x >= 0, "Age must be non-negative integer")
        )

        # Valid data should pass
        validator.validate({"name": "John", "age": 25})

        # Invalid name should fail
        with pytest.raises(ValidationError, match="Validation failed for field 'name'"):
            validator.validate({"name": 123, "age": 25})

        # Invalid age should fail
        with pytest.raises(ValidationError, match="Validation failed for field 'age'"):
            validator.validate({"name": "John", "age": -1})

    def test_validator_ignores_unvalidated_fields(self):
        """Test that validator ignores fields without rules."""
        validator = InputValidator()
        validator.add_rule("name", ValidationRule(lambda x: isinstance(x, str), "Must be string"))

        # Should pass even with extra fields
        validator.validate({"name": "John", "extra": "ignored"})


class TestValidateInputDecorator:
    """Test validate_input decorator."""

    def test_decorator_with_valid_input(self):
        """Test decorator with valid input."""

        @validate_input(
            name=[ValidationRule(lambda x: isinstance(x, str), "Must be string")],
            age=[ValidationRule(lambda x: isinstance(x, int), "Must be integer")],
        )
        def create_user(name, age):
            return f"User: {name}, Age: {age}"

        result = create_user(name="John", age=25)
        assert result == "User: John, Age: 25"

    def test_decorator_with_invalid_input(self):
        """Test decorator with invalid input."""

        @validate_input(name=[ValidationRule(lambda x: isinstance(x, str), "Must be string")])
        def create_user(name):
            return f"User: {name}"

        with pytest.raises(ValidationError, match="Must be string"):
            create_user(name=123)

    def test_decorator_with_single_rule(self):
        """Test decorator with single rule (not in list)."""

        @validate_input(name=ValidationRule(lambda x: isinstance(x, str), "Must be string"))
        def create_user(name):
            return f"User: {name}"

        result = create_user(name="John")
        assert result == "User: John"

        with pytest.raises(ValidationError):
            create_user(name=123)


class TestValidationRules:
    """Test pre-built validation rules."""

    def test_non_empty_string(self):
        """Test non_empty_string rule."""
        rule = ValidationRules.non_empty_string()

        # Valid strings
        rule.validate("hello")
        rule.validate("  hello  ")

        # Invalid values
        with pytest.raises(ValidationError):
            rule.validate("")
        with pytest.raises(ValidationError):
            rule.validate("   ")
        with pytest.raises(ValidationError):
            rule.validate(123)

    def test_max_length(self):
        """Test max_length rule."""
        rule = ValidationRules.max_length(5)

        # Valid lengths
        rule.validate("hello")
        rule.validate("hi")
        rule.validate("")

        # Invalid length
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            rule.validate("toolong")

    def test_min_length(self):
        """Test min_length rule."""
        rule = ValidationRules.min_length(3)

        # Valid lengths
        rule.validate("hello")
        rule.validate("abc")

        # Invalid length
        with pytest.raises(ValidationError, match="must be at least"):
            rule.validate("hi")

    def test_valid_url(self):
        """Test valid_url rule."""
        rule = ValidationRules.valid_url()

        # Valid URLs
        rule.validate("http://example.com")
        rule.validate("https://example.com")
        rule.validate("https://example.com/path?query=value")

        # Invalid URLs
        with pytest.raises(ValidationError):
            rule.validate("ftp://example.com")
        with pytest.raises(ValidationError):
            rule.validate("example.com")
        with pytest.raises(ValidationError):
            rule.validate("not-a-url")

    def test_safe_filename(self):
        """Test safe_filename rule."""
        rule = ValidationRules.safe_filename()

        # Valid filenames
        rule.validate("document.txt")
        rule.validate("my_file.pdf")
        rule.validate("file-name.doc")

        # Invalid filenames
        with pytest.raises(ValidationError):
            rule.validate("../etc/passwd")
        with pytest.raises(ValidationError):
            rule.validate("file/with/slashes.txt")
        with pytest.raises(ValidationError):
            rule.validate("file\\with\\backslashes.txt")
        with pytest.raises(ValidationError):
            rule.validate("file:with:colons.txt")

    def test_safe_path(self):
        """Test safe_path rule."""
        rule = ValidationRules.safe_path()

        # Valid paths
        rule.validate("documents/file.txt")
        rule.validate("folder/subfolder/file.txt")
        rule.validate("file.txt")

        # Invalid paths
        with pytest.raises(ValidationError):
            rule.validate("../etc/passwd")
        with pytest.raises(ValidationError):
            rule.validate("/absolute/path")
        with pytest.raises(ValidationError):
            rule.validate("folder/../other/file.txt")

    def test_alphanumeric(self):
        """Test alphanumeric rule."""
        rule = ValidationRules.alphanumeric()

        # Valid values
        rule.validate("abc123")
        rule.validate("ABC")
        rule.validate("123")

        # Invalid values
        with pytest.raises(ValidationError):
            rule.validate("abc-123")
        with pytest.raises(ValidationError):
            rule.validate("abc 123")
        with pytest.raises(ValidationError):
            rule.validate("abc@123")

    def test_regex_pattern(self):
        """Test regex_pattern rule."""
        rule = ValidationRules.regex_pattern(r"^[A-Z]{2,3}$", "Must be 2-3 uppercase letters")

        # Valid values
        rule.validate("AB")
        rule.validate("ABC")

        # Invalid values
        with pytest.raises(ValidationError, match="Must be 2-3 uppercase letters"):
            rule.validate("ab")
        with pytest.raises(ValidationError):
            rule.validate("ABCD")
        with pytest.raises(ValidationError):
            rule.validate("A1")

    def test_one_of(self):
        """Test one_of rule."""
        rule = ValidationRules.one_of(["red", "green", "blue"])

        # Valid values
        rule.validate("red")
        rule.validate("green")
        rule.validate("blue")

        # Invalid values
        with pytest.raises(ValidationError, match="must be one of"):
            rule.validate("yellow")
        with pytest.raises(ValidationError):
            rule.validate("Red")

    def test_integer_range(self):
        """Test integer_range rule."""
        rule = ValidationRules.integer_range(min_val=1, max_val=10)

        # Valid values
        rule.validate(1)
        rule.validate(5)
        rule.validate(10)

        # Invalid values
        with pytest.raises(ValidationError, match="minimum 1"):
            rule.validate(0)
        with pytest.raises(ValidationError, match="maximum 10"):
            rule.validate(11)
        with pytest.raises(ValidationError, match="must be an integer"):
            rule.validate("5")

    def test_integer_range_min_only(self):
        """Test integer_range rule with minimum only."""
        rule = ValidationRules.integer_range(min_val=0)

        rule.validate(0)
        rule.validate(100)

        with pytest.raises(ValidationError):
            rule.validate(-1)

    def test_integer_range_max_only(self):
        """Test integer_range rule with maximum only."""
        rule = ValidationRules.integer_range(max_val=100)

        rule.validate(-100)
        rule.validate(100)

        with pytest.raises(ValidationError):
            rule.validate(101)

    def test_email(self):
        """Test email rule."""
        rule = ValidationRules.email()

        # Valid emails
        rule.validate("user@example.com")
        rule.validate("test.email+tag@domain.co.uk")
        rule.validate("user123@test-domain.org")

        # Invalid emails
        with pytest.raises(ValidationError):
            rule.validate("invalid-email")
        with pytest.raises(ValidationError):
            rule.validate("@example.com")
        with pytest.raises(ValidationError):
            rule.validate("user@")
        with pytest.raises(ValidationError):
            rule.validate("user@domain")


class TestValidationIntegration:
    """Test validation integration scenarios."""

    def test_complex_validation_scenario(self):
        """Test complex validation with multiple rules and fields."""

        @validate_input(
            username=[RULES.non_empty_string(), RULES.min_length(3), RULES.max_length(20), RULES.alphanumeric()],
            email=[RULES.non_empty_string(), RULES.email()],
            age=[RULES.integer_range(min_val=13, max_val=120)],
        )
        def register_user(username, email, age):
            return {"username": username, "email": email, "age": age}

        # Valid registration
        result = register_user(username="john123", email="john@example.com", age=25)
        assert result["username"] == "john123"

        # Invalid username (too short)
        with pytest.raises(ValidationError, match="must be at least 3 characters"):
            register_user(username="jo", email="john@example.com", age=25)

        # Invalid email
        with pytest.raises(ValidationError, match="valid email address"):
            register_user(username="john123", email="invalid", age=25)

        # Invalid age
        with pytest.raises(ValidationError, match="minimum 13"):
            register_user(username="john123", email="john@example.com", age=10)

    def test_validation_error_context(self):
        """Test that validation errors include proper context."""
        validator = InputValidator()
        validator.add_rule("field", ValidationRule(lambda x: x > 0, "Must be positive"))

        try:
            validator.validate({"field": -5})
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "field 'field'" in str(e)
            assert e.context["field"] == "field"
            assert e.context["value"] == "-5"
