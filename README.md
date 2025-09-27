# MCP Rules Server

This is a MCP server that provides developer support by providing a common resource for AI agents with hybrid file access, HTTP caching, and persistent project configuration.

## What is this MCP Server for?

This is a developer convenience. It centralises how AI agent instructions are served, regardless which one you happen to be using.

This MCP server works with:
  - AmazonQ
  - Claude Code
  - github copilot (in VSCode & Jetbrains IDEs)
  - gemini

Since I use multiple (often switching between the first three), I needed a common place I could store AI agent instructions. I used symlinks at first, but this became a little unwieldy to manage, copying files between directories and keeping them updated whenever they changed.

Every AI client has its own idea of where to source instructions by default, and some of the implementations or versions from the same vendor often disagree with each other or just aren't consistent. This was my solution. This also keeps these docs in a central location plus it can keep them out of the project itself.

### The Implementation

Documents are split into three types:
- **Guidelines**: General developer guidelines. I love TDD nd doing things quickly in small iterations - even if I dislike doing it without AI assistance). It is great for keeping an AI bounded and restricted to doing stuff that's actually useful and to have some assurance that what it is implementing is actually what you want. Your guidelines most likely differ considerably from mine.
- **Language**: Programming languages each have their naunces. I develop in several, and

## Installation

```bash
# Install from source
git clone <repository-url>
cd mcp-server-guide
uv sync
uv run pip install -e .
```

## Usage

### Command Line Interface

The `mcp-server-guide` command provides a configurable MCP server with support for CLI arguments, environment variables, and sensible defaults.

```bash
# Start with defaults
mcp-server-guide

# Custom paths
mcp-server-guide --docroot /path/to/docs --guidesdir custom_guides/ --langsdir languages/

# Use short options
mcp-server-guide -d /docs -g guides/ -l langs/ -L python -c contexts/
```

### CLI Options

| Short | Long           | Environment Variable | Default              | Description                           |
| ----- | -------------- | -------------------- | -------------------- | ------------------------------------- |
| `-d`  | `--docroot`    | `MG_DOCROOT`         | `.`                  | Document root directory               |
| `-g`  | `--guidesdir`  | `MG_GUIDEDIR`        | `guide/`             | Guidelines directory                  |
| `-G`  | `--guide`      | `MG_GUIDE`           | `guidelines`         | Guidelines file (also --guidelines)   |
| `-l`  | `--langsdir`   | `MG_LANGDIR`         | `lang/`              | Languages directory                   |
| `-L`  | `--lang`       | `MG_LANGUAGE`        | `none` (auto-detect) | Language file (also --language)       |
| `-c`  | `--contextdir` | `MG_CONTEXTDIR`      | `context/`           | Context directory                     |
| `-C`  | `--context`    | `MG_CONTEXT`         | `project-context`    | Project context file                  |
|       | `--config`     | `MG_CONFIG`          | `.mcp-server-guide.config.json` | Configuration file path |
|       | `--global`     | `MG_CONFIG_GLOBAL`   | `false`              | Use global configuration file         |

### Language Auto-Detection

The server automatically detects your project's programming language when `--lang` is not specified or set to `none`. Supports 15+ languages:

- **Build file detection**: `Cargo.toml` → Rust, `pyproject.toml` → Python, `go.mod` → Go
- **Multi-language projects**: `build.gradle` → Java/Kotlin/Scala (analyzes source files)
- **Source file detection**: `*.swift` → Swift, `*.cs` → C#, `*.dart` → Dart, `*.sh` → Shell, etc.

### Environment Variables

Set environment variables to configure default behavior:

```bash
# Set custom paths
export MG_DOCROOT="/path/to/documentation"
export MG_GUIDEDIR="/path/to/guidelines"
export MG_LANGDIR="/path/to/languages"

# Start server (will use environment variables)
mcp-server-guide

# Override specific options (CLI takes precedence)
mcp-server-guide --docroot /different/path
```

### Configuration Files

The server supports flexible configuration file management:

```bash
# Use custom config file
mcp-server-guide --config /path/to/my-config.json

# Use global config (platform-specific)
mcp-server-guide --global

# Set via environment
export MG_CONFIG="/path/to/config.json"
export MG_CONFIG_GLOBAL="1"
```

**Global config locations:**
- Unix: `$HOME/.config/mcp-server-guide/config.json`
- Windows: `%APPDATA%/mcp-server-guide/config.json`

### Path Resolution

The server supports both absolute and relative paths:

- **Absolute paths** (starting with `/`) are used as-is
- **Relative paths** are resolved relative to the document root
- **File paths** without extensions automatically get `.md` extension
- **Directory paths** ending with `/` preserve the trailing slash

Examples:

```bash
# Absolute paths
mcp-server-guide --guide /absolute/path/to/guidelines.md

# Relative paths (resolved relative to docroot)
mcp-server-guide --docroot /docs --guide team/guidelines  # → /docs/team/guidelines.md

# Directory paths
mcp-server-guide --guidesdir custom_guides/  # Preserves trailing slash
```

## Examples

### Basic Usage

```bash
# Start with all defaults (language auto-detected)
mcp-server-guide

# Custom documentation root
mcp-server-guide --docroot /path/to/docs

# Multiple custom paths
mcp-server-guide \
  --docroot /docs \
  --guidesdir team_guides/ \
  --guide coding_standards \
  --langsdir programming_languages/ \
  --lang python
```

### Environment-Based Configuration

```bash
# Set up environment
export MG_DOCROOT="/company/docs"
export MG_GUIDEDIR="/company/docs/guidelines"
export MG_LANGDIR="/company/docs/languages"
export MG_LANGUAGE="typescript"

# Start server with environment config
mcp-server-guide

# Override specific options
mcp-server-guide --lang python
```

### Development Workflow

```bash
# Development environment
export MG_DOCROOT="./docs"
export MG_GUIDEDIR="./docs/dev-guides"

# Start development server
mcp-server-guide

# Production environment
mcp-server-guide \
  --docroot /prod/docs \
  --guidesdir /prod/docs/guidelines
```

## Troubleshooting

### Common Issues

**Issue**: `No such option: --langdir`
**Solution**: Use `--langsdir` (note the 's') for consistency with other directory options.

**Issue**: Configuration not taking effect
**Solution**: Check configuration precedence - CLI args override environment variables. Use `mcp-server-guide --help` to see all available options.

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
mcp-server-guide --docroot /custom --guide my-guide
# Output: Starting MCP server with config: {'docroot': '/custom', 'guide': 'my-guide', ...}
```

### Validation

The server validates all paths at startup:

- Files must exist and be actual files
- Directories must exist and be actual directories
- Invalid configurations will cause startup to fail with descriptive errors

## Migration Guide

### Environment Variables
If you were using any environment variables, update the prefix:
- `MCP_*` → `MG_*` (e.g., `MCP_DOCROOT` → `MG_DOCROOT`)

### Configuration Fields
- `projdir` → `contextdir` (directory renamed)
- `project` → `context` (file renamed)

### Language Detection
- Language now defaults to `none` (auto-detect) instead of empty
- Auto-detection supports 15+ languages based on project files
- Set `--lang none` to explicitly enable auto-detection

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test categories
uv run pytest tests/mcp_server_guide/  # Unit tests
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

## Technical Documentation

For technical details about the architecture and implementation, see [ARCHITECTURE.md](ARCHITECTURE.md).
