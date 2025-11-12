# MCP Guide Server

This is a MCP server that provides developer support by providing a common resource for AI agents.

## What is this MCP Server for?

This MCP is more than a developer convenience. It centralises how AI agent instructions are served, regardless which one you happen to be using.

This MCP server is designed to work with:

- AmazonQ
- Claude Code
- github copilot (in VSCode & Jetbrains IDEs)
- gemini
- possibly copilot cli

Since I use multiple agents (often switching between the first three), I needed a common place I could store AI agent instructions. I used symlinks at first, but this became a little unwieldy to manage, sometimes needing to copy files between directories and keeping them updated whenever they changed.

Every AI client has its own idea of where to source instructions, and some of the implementations or versions from the same vendor often disagree with each other or just aren't consistent. This was my solution. This also keeps prompts in a central location plus it can keep them out of the project itself.

## The Objective

Prompts are key to keeping an agentic agent within working guidelines. Without them, the agent will implement your instructions (usually) plus some, based on the temperature and tuning of its LLM. When provided with an idea, the agent will immediately start making changes regardless of it having only incomplete context, knowledge of past events and eften giving little regard for duplicating code, breaking encapsulation or going about things completely different from elsewhere in the codebase.

This MCP is a step towards providing the AI with guardrails that it cannot (or should not) ignore in the hope of providing more deterministic behaviour and output. This solution is not guaranteed, and AI will sometimes completely ignore instructions.

### The Implementation

Documents containing prompts are served to the AI for its consumption. These take the form of general guidelines,

Documents are organized using a **unified categories system**. The following three default categories are created when a project is first instantiated - implicitly, when started in a new project:, using using the switch_project tool with a different name.

- **guide**: General developer guidelines (TDD methodology, coding standards, workflow requirements)
- **lang**: Programming language-specific guidelines (syntax, best practices, tooling, project structure)
- **context**: Project-specific information (issue management, specifications, workflow details)
- **prompt**: AI prompts shown by various built in `@guide --action` prompts that override the builtin default.

These are all regular categories that can be customized, removed or renamed like any other category through the configuration system. However the `prompt` category is special in that this category is checked for a file that corresponds to a `@guide --action` otherwise it will use the built-in ones.

## Docker Usage

The MCP Server Guide is available as Docker containers for both development and production use.

### Quick Start

```bash
# Build and run development container
docker compose up mcp-server-guide-dev

# Build and run production container
docker compose up mcp-server-guide-prod

# Or build manually
docker build -f Dockerfile.dev -t mcp-server-guide:dev .
docker build -f Dockerfile.prod -t mcp-server-guide:prod .
```

### Container Details

- **Base Image**: `python:3.14-alpine3.22`
- **User**: Non-root user `mcp`
- **Working Directory**: `/home/mcp/mcp-server-guide`
- **Communication**: stdio (MCP protocol)

### Environment Variables

- `MCP_LOG_LEVEL`: Set log level (default: `info` for prod, `debug` for dev)

### Development vs Production

- **Development** (`Dockerfile.dev`): Includes all dev tools (pytest, mypy, ruff, etc.)
- **Production** (`Dockerfile.prod`): Multi-stage build with minimal runtime footprint

### Volume Mounting (Development)

Uncomment the volume mount in `compose.yaml` for live development:

```yaml
volumes:
  - .:/home/mcp/mcp-server-guide
```

## Installation

### From Source

```bash
# Install from source
git clone <repository-url>
cd mcp-server-guide
uv sync
uv run pip install -e .
```

### From PyPI

```bash
# Install from PyPI
pip install mcp-server-guide
```

### Installing Templates

After installing the package, you need to install the templates to a location of your choice. The package includes a dedicated installation script for this purpose:

```bash
# Install templates to the default location (~/.local/share/mcp-server-guide/templates)
mcp-server-guide-install

# Install templates to a custom location
mcp-server-guide-install --templates-dir /path/to/your/templates

# Enable verbose output for more detailed installation logs
mcp-server-guide-install -v
```

The installation script will:
1. Copy all template files to the specified directory
2. Create a configuration file at `~/.config/mcp-server-guide/config.yaml` (if it doesn't exist)
3. Set the `docroot` parameter in the config file to point to the templates directory

This ensures that when you run the mcp-server-guide command, it will automatically find and use the installed templates.

## Usage

### Command Line Interface

The `mcp-server-guide` command provides a configurable MCP server.

```bash
# Start with defaults
mcp-server-guide

# Custom document root
mcp-server-guide --docroot /path/to/docs

# With configuration file
mcp-server-guide --config /path/to/config.json
```

By default, this mcp runs in "stdio" mode (the only mode currently supported). It converses with the AI agent using the established MCP protocol which uses jsonrpc version 2.0.

### CLI Options


| Short | Long               | Description                                                  |
| ----- | ------------------ | ------------------------------------------------------------ |
| `-c`  | `--config`         | Configuration file path                                      |
| `-d`  | `--docroot`        | Document root directory (default:`.`)                        |
| -C    | `--log-console`    | Enable console logging (default: true unless file specified) |
| -N    | `--no-log-console` | Disable console logging                                      |
| -F    | `--log-file`       | Log file path (empty for no file logging)                    |
| -J    | `--log-json`       | Enable JSON structured logging to file                       |
| -L    | `--log-level`      | Logging level (DEBUG, INFO, WARN, ERROR, OFF)                |
| -v    | `--version`        | Show version and exit                                        |
| -h    | `--help`           | Show help message and exit                                   |

### Configuration

The `GUIDE_TOOL_PREFIX` environment variable controls how MCP tools are named:

```bash
# Default behavior - tools prefixed with "guide_"
# Tools: guide_get_current_project, guide_get_category_content, guide_get_guide, etc.
# (No environment variable set or explicitly set to "guide_")
export GUIDE_TOOL_PREFIX="guide_"

# Remove prefix for clients that auto-namespace tools (e.g., Claude Code)
# Tools: get_current_project, get_category_content, get_guide, etc.
export GUIDE_TOOL_PREFIX=""

# Use custom prefix for specific clients
export GUIDE_TOOL_PREFIX="myprefix_"
```

**Why this matters:**

- **Amazon Q** does not automatically namespace MCP tools, so the `guide_` prefix prevents name collisions with other MCP servers
- **Claude Code** automatically namespaces tools by server name, so the prefix is redundant and can be removed by setting `GUIDE_TOOL_PREFIX=""`
- Other clients may have different behaviors - adjust the prefix accordingly

## API Reference

### Tools

#### `get_guide(category_or_collection, document, project=None)`

Retrieve guide content for a specific document in a category or collection.

**Parameters:**

- `category_or_collection` (string): Name of the category or collection to search
- `document` (string): Name of the document to retrieve
- `project` (string, optional): Project name (defaults to current project)

**Returns:** String content of the document, or `None` if not found

**Examples:**

```python
# Get a specific document from the 'guide' category
content = await get_guide("guide", "guidelines")

# Get language-specific guidelines
content = await get_guide("lang", "python")

# Get project context information
content = await get_guide("context", "project-context")
```

### Prompts

#### `@guide` Prompt

Get comprehensive guide content, specific category content, or execute CLI commands for advanced operations.

**Basic Usage:**

```
@guide                    # Get help and overview of all available categories
@guide category_name      # Get all content from a specific category
@guide collection_name    # Get all content from a specific collection
```

## CLI Commands

The `@guide` prompt supports a powerful CLI syntax for advanced operations:

### Quick Reference

| Short | Long        | Description                    |
|-------|-------------|--------------------------------|
| `-h`  | `--help`    | Show help (general or target-specific) |
| `-T`  | `--content` | Inline text content           |
| `-C`  | `--category`| Category target/argument       |
| `-D`  | `--document`| Document target                |
| `-M`  | `--collection`| Collection target            |
| `-n`  | `--name`    | Name argument                  |
| `-f`  | `--file`    | File path argument             |

### Phase Commands

Phase commands help manage development workflow transitions:

```
@guide -d "topic"         # Enter discussion phase with context
@guide -p "task details"  # Enter planning phase with task context
@guide -i "implementation notes" # Enter implementation phase
@guide -c "check details" # Enter check/validation phase
@guide -s                 # Show current project status
@guide -q "search term"   # Search across all content
```

### CRUD Operations

#### Category Operations
```
@guide -C -l                                           # List all categories
@guide -C -a --name "docs" --dir "docs/"               # Add category
@guide -C -r "old-category"                            # Remove category
@guide -C -h                                           # Category help
```

#### Collection Operations
```
@guide -M -l                                           # List all collections
@guide -M -a --name "backend" --categories "api,db"    # Add collection
@guide -M -A "backend" --categories "auth"             # Add categories to collection
@guide -M -h                                           # Collection help
```

#### Document Operations
```
@guide -D -l --category "docs"                         # List documents in category
@guide -D -a "readme" --category "docs" --content "Hello" # Add document
@guide -D -a --name "guide" --category "docs" --file "guide.md" # Add from file
@guide -D -h                                           # Document help
```

### Concatenation Support

Combine multiple short flags for concise commands:

```
@guide -DaT -n "readme" -C "docs" -T "Hello world"     # Add document (concatenated)
@guide -Cal --name "api" --dir "api/"                  # Add category (concatenated)
@guide -Ml                                             # List collections (concatenated)
```

### Target-Specific Help

Get focused help for specific operations:

```
@guide -D -h              # Document operations help
@guide -C -h              # Category operations help
@guide -M -h              # Collection operations help
@guide --document --help  # Same as -D -h
```

**Parameters:**

- `category` (optional): Name of the category to retrieve content from
- CLI flags and arguments as documented above

**Examples:**

1. **Get help and overview:**

   ```
   @guide
   ```

   Returns: Complete help system with available categories, collections, and usage instructions.

2. **Get specific category content:**

   ```
   @guide guide
   ```

   Returns: All content from the 'guide' category (coding standards, workflows, etc.)

   ```
   @guide lang
   ```

   Returns: All language-specific guidelines and best practices.

   ```
   @guide context
   ```

   Returns: All project-specific context and information.

3. **Get custom category content:**

   ```
   @guide my-custom-category
   ```

   Returns: All content from your custom category.

4. **CLI Operations Examples:**

   ```
   @guide -C -l                                    # List all categories
   @guide -D -a "readme" -C "docs" -T "# README"  # Add document with content
   @guide -M -a "backend" --categories "api,db"   # Create collection
   @guide -DaT -n "guide" -C "docs" -T "content"  # Concatenated form
   ```

**Error Handling:**

- If category doesn't exist: Returns error message with details
- If category is empty: Returns empty content
- If no category specified: Returns comprehensive help
- CLI validation errors: Returns specific guidance and examples

### Resources

MCP resources provide a standardized way to access category and collection content through URI-based addressing.

#### Resource URIs

The server exposes resources using the `guide://` URI scheme:

- **Categories**: `guide://category/{category_name}`
- **Collections**: `guide://collection/{collection_name}`
- **Help**: `guide://help`

#### Category Resources

Each category is automatically registered as an MCP resource when the server starts:

```
guide://category/guide     - Access the 'guide' category content
guide://category/lang      - Access the 'lang' category content
guide://category/context   - Access the 'context' category content
guide://category/my-custom - Access custom category content
```

#### Collection Resources

Collections are also exposed as resources:

```
guide://collection/my-collection - Access collection content
```

#### Resource Content

When accessed, category resources return:

- All documents matching the category's patterns
- Managed documents from the category's `__docs__/` directory
- Combined content formatted for AI consumption

Collection resources return content from all categories within the collection.

### Configuration Files

The server supports flexible configuration file management in yaml format
