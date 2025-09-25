# MCP Rules Server

This is a MCP server that provides developer support by providing a common resource for AI agents with hybrid file access, HTTP caching, and persistent project configuration.

## 🏗️ **Architecture**

### **Hybrid File Access System**
```python
# Supports all file source types with intelligent caching
server = create_server(cache_dir="/tmp/cache")

# URL schemes supported:
# - local:./path (client filesystem)
# - server:./path (server filesystem)
# - file://./path (context-aware files)
# - https://example.com/path (HTTP with caching & validation)
# - ./path (context-aware defaults)
```

### **Persistent Configuration**
```python
# Automatic project detection and configuration
config = ProjectConfig(
    project="my-app",
    guide="https://wiki.company.com/guide.md",
    language="typescript",
    tools=["eslint", "jest"]
)

# Saves to .mcpguide.config.json in project root
manager = ProjectConfigManager()
manager.save_config(Path("."), config)

# Real-time file watching
watcher = manager.watch_config(project_root, on_config_change)
```

### **Session Management**
```python
# Context-aware session handling
session = SessionManager()
session.load_project_from_path(project_root)
effective_config = session.get_effective_config("my-app")
```

## Installation

```bash
# Install from source
git clone <repository-url>
cd mcpguide
uv sync
uv run pip install -e .
```

## Usage

### Command Line Interface

The `mcpguide` command provides a configurable MCP server with support for CLI arguments, environment variables, and sensible defaults.

```bash
# Start with defaults
mcpguide

# Customize paths
mcpguide --docroot /path/to/docs --guidesdir custom_guides/ --langsdir languages/

# Use short options
mcpguide -d /docs -g guides/ -l langs/ -L python -p projects/
```

### CLI Options

| Short | Long | Environment Variable | Default | Description |
|-------|------|---------------------|---------|-------------|
| `-d` | `--docroot` | `MCP_DOCROOT` | `.` | Document root directory |
| `-g` | `--guidesdir` | `MCP_GUIDEDIR` | `guide/` | Guidelines directory |
| `-G` | `--guide` | `MCP_GUIDE` | `guidelines` | Guidelines file (also --guidelines) |
| `-l` | `--langsdir` | `MCP_LANGDIR` | `lang/` | Languages directory |
| `-L` | `--lang` | `MCP_LANGUAGE` | `` | Language file (also --language) |
| `-p` | `--projdir` | `MCP_PROJDIR` | `project/` | Project directory |
| `-P` | `--project` | `MCP_PROJECT` | `<current-dir-name>` | Project context file (also --context) |

### Configuration Precedence

Configuration values are resolved in the following order (highest to lowest priority):

1. **CLI Arguments** - Explicitly provided command line options
2. **Environment Variables** - Environment variables with `MCP_` prefix
3. **Persistent Configuration** - `.mcpguide.config.json` files
4. **Session Overrides** - Runtime session modifications
5. **Defaults** - Built-in default values

### Environment Variables

Set environment variables to configure default behavior:

```bash
# Set custom paths
export MCP_DOCROOT="/path/to/documentation"
export MCP_GUIDEDIR="/path/to/guidelines"
export MCP_LANGDIR="/path/to/languages"

# Start server (will use environment variables)
mcpguide

# Override specific options (CLI takes precedence)
mcpguide --docroot /different/path
```

### Path Resolution

The server supports both absolute and relative paths:

- **Absolute paths** (starting with `/`) are used as-is
- **Relative paths** are resolved relative to the document root
- **File paths** without extensions automatically get `.md` extension
- **Directory paths** ending with `/` preserve the trailing slash

Examples:
```bash
# Absolute paths
mcpguide --guide /absolute/path/to/guidelines.md

# Relative paths (resolved relative to docroot)
mcpguide --docroot /docs --guide team/guidelines  # → /docs/team/guidelines.md

# Directory paths
mcpguide --guidesdir custom_guides/  # Preserves trailing slash
```

### Project Context

The `--project` option defaults to the current directory name, making it easy to have project-specific configurations:

```bash
# In /path/to/my-awesome-project/
mcpguide  # project defaults to "my-awesome-project"

# Override project context
mcpguide --project custom-context
```

## Examples

### Basic Usage

```bash
# Start with all defaults
mcpguide

# Custom documentation root
mcpguide --docroot /path/to/docs

# Multiple custom paths
mcpguide \
  --docroot /docs \
  --guidesdir team_guides/ \
  --guide coding_standards \
  --langsdir programming_languages/ \
  --lang python
```

### Environment-Based Configuration

```bash
# Set up environment
export MCP_DOCROOT="/company/docs"
export MCP_GUIDEDIR="/company/docs/guidelines"
export MCP_LANGDIR="/company/docs/languages"
export MCP_LANGUAGE="typescript"

# Start server with environment config
mcpguide

# Override specific options
mcpguide --lang python --project special-project
```

### Development Workflow

```bash
# Development environment
export MCP_DOCROOT="./docs"
export MCP_GUIDEDIR="./docs/dev-guides"

# Start development server
mcpguide --project dev-environment

# Production environment
mcpguide \
  --docroot /prod/docs \
  --guidesdir /prod/docs/guidelines \
  --project production-system
```

## Troubleshooting

### Common Issues

**Issue**: `No such option: --langdir`
**Solution**: Use `--langsdir` (note the 's') for consistency with other directory options.

**Issue**: Configuration not taking effect
**Solution**: Check configuration precedence - CLI args override environment variables. Use `mcpguide --help` to see all available options.

**Issue**: File not found errors
**Solution**: Ensure all specified paths exist. The server validates file and directory existence at startup.

**Issue**: Path resolution problems
**Solution**:
- Use absolute paths for explicit control
- Ensure relative paths are correct relative to `--docroot`
- Check that file extensions are correct (`.md` is added automatically for files without extensions)

### Debugging

Enable verbose output to see resolved configuration:

```bash
# The server shows the final resolved configuration
mcpguide --docroot /custom --guide my-guide
# Output: Starting MCP server with config: {'docroot': '/custom', 'guide': 'my-guide', ...}
```

### Validation

The server validates all paths at startup:
- Files must exist and be actual files
- Directories must exist and be actual directories
- Invalid configurations will cause startup to fail with descriptive errors

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test categories
uv run pytest tests/mcpguide/  # Unit tests
uv run pytest tests/test_integration.py  # Integration tests
```

### Code Quality

```bash
# Linting
uv run ruff check src tests

# Type checking
uv run mypy src

# Formatting
uv run ruff format src tests
```
