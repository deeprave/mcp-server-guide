# Python Guidelines

## Project Structure
**Standard layout with uv:**
```
root/
├── .python-version          # 3.13
├── .pre-commit-config.yaml  # pre-commit hooks
├── .coveragerc             # coverage configuration
├── pyproject.toml          # with pytest config
├── README.md
├── LICENSE.md
├── src/
│   ├── __init__.py         # required for pytest path resolution
│   └── <modulename>/
└── tests/
    ├── __init__.py         # required for pytest path resolution
    └── <modulename>/
```

**Note:** The `__init__.py` files in both `src/` and `tests/` directories are required for pytest to properly resolve import paths in the src layout.

## Formatting & Quality
- **Use `ruff format` and `ruff check`** - address warnings before considering complete
- **f-strings:** `f"Error: {e}"` vs `"Error: {}".format(e)`
- **Use `mypy`** for type checking
- **pre-commit hooks** ensure all commits are checked
- **Use PEP 8 conventions** _imports at the top of modules_ unless required to avoid circular dependencies
- Avoid large `if`/`elif`/`else` blocks with more than 1 `elif`.
  se `match` instead, a dictionary or some form  of functional approach.

## Code Complexity
- **Early returns** with guard clauses
- **List/dict comprehensions** over loops when this produces readable code
- **Chain operations** - avoid intermediate variables
  - return a function result directly if last statement in a function or method
  - use the walrus operator if the only reason for the variable is for an `if` or `while` statement or expression

## Type Hints
- **Use modern typing:** `List[str]`, avoid use if `Any` if possible
- **Function signatures:** Always type parameters and returns
- **Use `typing.Protocol`** for structural typing
- **`Optional[T]` or `T | None`** for nullable types

## Code Quality checks
- **For Oython, use the following code quality tools**
  - linting → ruff check
  - type checking → mypy
  - testing → pytest
  - security → osvcheck (if available)

## Iterator Patterns
**Prefer comprehensions and generators:**
```python ignore
# Good
valid_items = [item.process() for item in items if item.is_valid()]

# Avoid
results = []
for item in items:
    if item.is_valid():
        results.append(item.process())
```

## Imports
- **Use imports at module level** - follow PEP 8 standards
- Only use function/class level imports to avoid circular imports & similar

## Error Handling
- **Use specific exceptions** - DO NOT USE bare `except:` or `except Exception:`
- **Context managers** for resource management
- **`raise ... from e`** - preserve exception chains
- **Custom exceptions** for domain-specific errors

## Pattern Matching (Python 3.11+)
- **Use `match/case`** for complex conditionals
- **Structural pattern matching** for data extraction
- **Guard clauses** with `if` conditions in patterns

## Collections
- **Choose correctly:** `list`, `dict`, `set`, `deque`, `Counter`
- **Use `collections.defaultdict`** to avoid key checks
- **`frozenset`** for immutable sets

## Function Design
- **Small, focused functions** with single responsibility
- **Use `*args, **kwargs`** judiciously
- **Default arguments** should be immutable
- **Use `functools.lru_cache`** for expensive pure functions

## Classes & Objects
- **Use `@dataclass`** for simple data containers
- **`__slots__`** for memory efficiency when needed
- **Properties** over getters/setters
- **Context managers** with `__enter__`/`__exit__`

## Testing with pytest
**Always configure in `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
]
```

## Project Configuration
**Essential `pyproject.toml` sections:**
```toml
[project]
name = "modulename"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "ruff", "mypy", "pre-commit"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
src = ["src"]
target-version = "py313"

[tool.mypy]
python_version = "3.13"
packages = ["src"]
strict = true
```

### Testing
#### TDD

If using TDD, tests should be written before the implementation. Sometimes those tests may not be optimal for ongoing testing or regression testing.
So here are some general guidelines.

##### Refactoring or Redesign

Again, if using TDD, some tests are required to be written to test a refactoring or other re-arrangement (removing code or changes in design).
These should be regarded as "throwaway" tests as in the end, once the task is done and the tests pass to confirm successful completion they may serve no useful purpose going forwards. Those tests may be removed. Instead, replace with tests that actually TEST something useful about the resulting code, if required - and not already covered.

##### Coverage

Don't write tests just to achieve code coverage. Instead, test something in a useful way - that functionality works, that something returns or is set to a correct value etc. Certainly do not name tests, classes or modules containing the word _coverage_ - this is a bad smell that this module contains artificial tests purely to enhance or provide coverage. Tests should test actual functionality, and do not exist to achieve an arbitrary statistic.


**Essential `.pre-commit-config.yaml`:**
```yaml
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: no-commit-to-branch
        args: ['--branch', 'main']
        exclude: '^main$'
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: requirements-txt-fixer

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.6
    hooks:
      - id: ruff
        args:
          - --fix
          - --line-length=120

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest --cov --cov-config=.coveragerc
        language: system
        types: [python]
        pass_filenames: false

  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.24.1
    hooks:
      - id: validate-pyproject
```

**Essential `.coveragerc`:**
```ini
[run]
omit =
    */tests/conftest.py
    */tests/test_*.py

[report]
fail_under = 90
```

## Anti-Patterns
- **No bare `except:`** - catch specific exceptions
- **No mutable defaults** - use `None` and create in function
- **No `import *`** - explicit imports only
- **Address linter warnings** - don't ignore without reason
- **No `eval()` or `exec()`** without strong justification

## Common Idioms
```python  ignore
# Dictionary get with default
value = data.get('key', default_value)

# Enumerate for index and value
for i, item in enumerate(items):
    process(i, item)

# Context manager for files
with open(filename) as f:
    content = f.read()

# Exception chaining
try:
    risky_operation()
except SpecificError as e:
    raise CustomError("Operation failed") from e
```

## uv Commands
```bash
# Create new project
uv init --package <modulename>

# Add dependencies
uv add <package>
uv add --dev pytest pytest-cov ruff mypy pre-commit

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Format and lint
uv run ruff format src tests
uv run ruff check src tests
uv run mypy src

# Run pre-commit on all files
uv run pre-commit run --all-files

# Refresh installed package after MCP development changes
uv sync
```

## MCP Development Notes
When developing MCP servers with uv, you need to run `uv sync` to refresh the installed package after making changes. This ensures the MCP server picks up your latest code modifications.
