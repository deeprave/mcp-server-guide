# MCP Guide Server

This is a MCP server that provides developer support by providing a common resource for AI agents.

## What is this MCP Server for?

This MCP is more than a developer convenience. It centralises how AI agent instructions are served, regardless which one you happen to be using.

This MCP server works with:

- AmazonQ
- Claude Code
- github copilot (in VSCode & Jetbrains IDEs)
- gemini

Since I use multiple (often switching between the first three), I needed a common place I could store AI agent instructions. I used symlinks at first, but this became a little unwieldy to manage, copying files between directories and keeping them updated whenever they changed.

Every AI client has its own idea of where to source instructions by default, and some of the implementations or versions from the same vendor often disagree with each other or just aren't consistent. This was my solution. This also keeps these docs in a central location plus it can keep them out of the project itself.

## The Objective

Prompts are key to keeping an agentic agent within working guidelines. Without them, the agent will implement your instructions (usually) plus some, based on the temperature and tuning of its LLM. When provided with an idea, the agent will immediately start making changes regardless of it having incomplete context and knowledge of past events.

This MCP is a step towards providing the AI with guardrails that it cannot (or should not) ignore. This solution is not guaranteed, and AI will sometimes completely ignore instructions.

### The Implementation

Document are served to the AI for its consumption. These take the form of general guidelines,

Documents are organized using a **unified categories system** with three built-in categories:

- **guide**: General developer guidelines (TDD methodology, coding standards, workflow requirements)
- **lang**: Programming language-specific guidelines (syntax, best practices, tooling, project structure)
- **context**: Project-specific information (issue management, specifications, workflow details)

The CLI arguments (`--guidesdir`, `--guide`, `--langsdir`, `--lang`, `--contextdir`, `--context`) configure the appropriate built-in categories.

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


| Short | Long           | Environment Variable | Default                           | Description                                          |
| ----- | -------------- | -------------------- | --------------------------------- | ---------------------------------------------------- |
| `-d`  | `--docroot`    | `MG_DOCROOT`         | `.`                               | Document root directory                              |
| `-c`  | `--config`     | `MG_CONFIG`          | `[platform location]/config.json` | Configuration file path                              |
| `-g`  | `--guidesdir`  | `MG_GUIDEDIR`        | `guide/`                          | Guidelines directory (configures 'guide' category)   |
| `-G`  | `--guide`      | `MG_GUIDE`           | `guidelines`                      | Guidelines file (configures 'guide' category)        |
| `-l`  | `--langsdir`   | `MG_LANGDIR`         | `lang/`                           | Languages directory (configures 'lang' category)     |
| `-L`  | `--lang`       | `MG_LANGUAGE`        | `none` (auto-detect)              | Language file (configures 'lang' category)           |
|       | `--contextdir` | `MG_CONTEXTDIR`      | `context/`                        | Context directory (configures 'context' category)    |
| `-C`  | `--context`    | `MG_CONTEXT`         | `project-context`                 | Project context file (configures 'context' category) |

**platform location is one of**

- On Unix-like systems (incl MacOS, Linux): ~/.config/mcp-server-guide/
- On Windows: %APPDATA%/mcp-server-guide/

### Language Auto-Detection

On first startup on an unknown project, the server automatically detects your project's programming language when `--lang` is not specified or set to `none`. Supports 15+ languages:

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

The server supports flexible configuration file management in yaml format
