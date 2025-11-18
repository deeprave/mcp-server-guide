# MCP Guide Server

This MCP server that provides a repository of instructions and documentation. It supports an iterative and phased development cycle to support the developer through building software features.

## What is this MCP Server for?

This MCP is more than a developer convenience. It centralizes how AI agent instructions are served, regardless of which client you happen to be using. It should work with any agent that supports MCP servers.

## Background

Instructions and prompts are an **essential** part of using agentic AI constructively in a controlled, useful, and productive manner. So-called "vibe coding" is useful only for a tiny subset of tasks, such as a simple command line utility or script. Once you move into serious applications, even small ones, the context window and other factors make the approach prone to error, architecture that tends to be disjointed and often over-engineered, mixes concerns, and makes incorrect decisions based on guesses and ambiguities.

When used in a controlled manner, it is possible to make the result much more deterministic.

Since I use multiple agents (often switching between the first three), I needed a common place to store prompts and instructions. Initially, I used documents scattered across directories, but this became unwieldy to manage, sometimes needing to copy files between directories and trying to keep them updated whenever they were improved.

Every agentic client has its own idea of where to source instructions, and some implementations or versions from the same vendor often disagree with each other or lack consistency. `mcp-server-guide` is my solution. This keeps prompts and instructions in a central location and can keep them out of the project itself.

## The Objective

Prompts are key to keeping an agentic agent within working guidelines. Without them, the agent will implement your instructions (usually) plus some, based on the temperature and tuning of its LLM. When provided with an idea, the agent will immediately start making changes regardless of having only incomplete context, knowledge of past events, and often giving little regard for duplicating code, breaking encapsulation, or implementing changes in a completely different wat from elsewhere in the codebase.

This MCP is a step towards providing the AI with guardrails that it cannot (or should not) ignore in the hope of providing more deterministic behavior and output. This solution is not guaranteed, and AI will sometimes completely ignore instructions.

### The Implementation

`mcp-server-guide` supports a built-in iterative development cycle. It is designed to follow a four-step process using the following phases:

**Discussion**: This phase is for specifying requirements and ultimately what conditions must be satisfied to complete the feature to be implemented. Both the user and agent need to use this phase to arrive at alignment. The user makes it clear what needs to be done - and often, how it is to be done - and the agent needs to be clear. Not all issues that may arise during implementation may be sufficiently covered (or discovered) at this point, but any known assumptions should be stated.

**Planning**: To state the obvious, the planning phase is for planning. The objective of this phase is to produce assets in the form of specification documents, implementation plans, and/or checklists - or all three combined into a single document, depending on user preference. Documents are produced in markdown for readability by both the agent and user. Before transitioning to the next phase, the user must explicitly provide consent, which is essentially agreeing with the document(s) content.

> The reason for producing document artifacts in this phase provides several benefits:
> - A plan does not need to be executed immediately
> - A plan can be paused and resumed
> - Multiple plans can be queued, reordered, and enhanced over time
> - It is a point of reference regarding the implementation of a feature

**Implementation**: This phase, which requires explicit consent from the user, is where the agent executes the plan. Insist that the agent must periodically mark completed items on the checklist and mark anything that is deferred or "todo". Tests must be produced (in TDD mode, before implementation) and run after each individual task to ensure that the produced code works as it should.

**Check**: Automated software checks are run during this phase to ensure compliance with standards for the project. This also provides an opportunity for code review; to ensure that the implementation agrees with the user's intent, conformance to and completion of the implementation plan, and is in line with the overall project architecture.

Transition between phases is not automatic and is triggered when certain conditions are met, such as the existence and content of the `.consent` and `.issue` files. Nor is strict ordering required. The `@guide` prompt may be used to force transition to whichever phase the user thinks should apply.

## Quick Install

**Prerequisites:** Install `libmagic` system library first:
- macOS: `brew install libmagic`
- Ubuntu/Debian: `sudo apt-get install libmagic1`
- Fedora/RHEL: `sudo dnf install file-libs`
- Windows: `choco install file`

See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed installation instructions.

Get started quickly with agents that support JSON configuration:

```json
{
  "mcpServers": {
  ...
    "mcp-server-guide": {
      "command": "uvx",
      "args": ["mcp-server-guide"],
      "env": {
        "GUIDE_TOOL_PREFIX": ""
      }
    }
  ...
  }
}
```

Note: you need to install `uv` in your operating system to make the `uvx` command available.


### Initial Setup

After installation, the server will automatically create default categories on commencement of a new project. You can customize the configuration using the management functions described below.

### Environment Variables

- `GUIDE_TOOL_PREFIX`: Controls tool name prefixing (default: "guide_")
- `GUIDE_PROJECT_NAME`: Override default project detection
- `GUIDE_CONFIG_PATH`: Custom configuration file path

### First Steps with @guide

Once connected to your AI client, try these commands:

```
@guide help              # Show detailed help information
@guide category list     # List available categories
@guide guide            # Show general guidelines
@guide lang python      # Show Python-specific guidelines
```

## Core Usage

### @guide Prompt - Primary Interface

The `@guide` prompt is your main interface for accessing documentation and managing the development workflow.

#### Basic Commands

```
@guide help              # Show detailed help and available categories
@guide category_name     # Show content from a specific category
@guide collection_name   # Show content from a specific collection
```

#### Phase Commands

Control your development workflow with phase commands:

```
@guide discuss "topic"   # Start discussion phase with context
@guide plan "feature"    # Start planning phase with task details
@guide implement         # Start implementation phase
@guide check            # Start check/validation phase
```

#### Category Access

Access documentation by category:

```
@guide guide            # General development guidelines
@guide lang             # Language-specific guidelines
@guide context          # Project-specific information
@guide prompt           # Custom AI prompts
```

#### Collection Access

Collections group multiple categories for convenient access:

```
@guide backend          # Access backend-related categories
@guide frontend         # Access frontend-related categories
@guide testing          # Access testing-related categories
```

#### Category Concatenation

Reference multiple categories at once:

```
@guide api,database,auth    # Combine multiple categories
@guide lang,guide          # Language guidelines + general guidelines
```

## Management Functions

### AI Assistance Alternative

Instead of memorizing complex syntax, simply ask the AI what to do:

- *"Create a collection that includes both 'api' and 'database' categories"*
- *"Show me all available categories"*
- *"Remove the old 'legacy' category"*

The AI will use the appropriate management tools to fulfill your request.

### Category Management

Manage your documentation categories:

```
@guide category list                           # List all categories
@guide category add --name "testing" --dir "tests/" --patterns "*.test.js,*.spec.js"
@guide category update --name "testing" --description "Test files and documentation"
@guide category remove --name "old-category"
```

### Collection Management

Group categories into collections:

```
@guide collection list                         # List all collections
@guide collection add --name "backend" --categories "api,database,auth"
@guide collection update --name "backend" --categories "api,database,auth,logging"
@guide collection remove --name "old-collection"
```

### Document Management

Manage specific documents within categories:

```
@guide document list --category "docs"         # List documents in category
@guide document add --category "docs" --name "readme" --content "# Project README"
@guide document update --category "docs" --name "readme" --content "# Updated README"
@guide document remove --category "docs" --name "old-doc"
```

## Advanced Features

### Collections & Category Concatenation

**Collections** provide a powerful way to organize related documentation:

- Group multiple categories together for convenient access
- Create logical groupings like "backend", "frontend", "testing"
- Access comprehensive context with a single command
- Useful for organizing related documentation (e.g., "backend" collection including "api", "database", "auth" categories)

**Category Concatenation** allows referencing multiple categories:

- Use comma-separated category names: `@guide api,database,auth`
- Combines content from all specified categories
- Maintains logical organization while providing comprehensive context
- Perfect for complex tasks requiring multiple knowledge domains

### Document Management vs Pattern-Based Content

The system supports two types of content:

#### Pattern-Based Content
- Files matched by category patterns (e.g., `*.md` files in category directories)
- Automatically discovered based on file patterns
- Changes when files are added/removed from directories
- Dynamic and reflects current file system state

#### Managed Documents
- Specific documents created via document management functions
- Unaffected by pattern matching
- Can reference category/document names directly without requiring pattern matches
- Persistent until explicitly removed
- Ideal for stable, curated content

### Project Management

Switch between different projects and configurations:

```
@guide project list                    # List available projects
@guide project switch "my-project"     # Switch to a different project
@guide project config                  # Show current project configuration
```

## Configuration

### Command Line Options

| Short | Long               | Description                                                  |
| ----- | ------------------ | ------------------------------------------------------------ |
| `-c`  | `--config`         | Configuration file path                                      |
| `-d`  | `--docroot`        | Document root directory (default: `.`)                      |
| `-C`  | `--log-console`    | Enable console logging (default: true unless file specified) |
| `-N`  | `--no-log-console` | Disable console logging                                      |
| `-F`  | `--log-file`       | Log file path (empty for no file logging)                   |
| `-J`  | `--log-json`       | Enable JSON structured logging to file                       |
| `-L`  | `--log-level`      | Logging level (DEBUG, INFO, WARN, ERROR, OFF)               |
| `-v`  | `--version`        | Show version and exit                                        |
| `-h`  | `--help`           | Show help message and exit                                   |

### Configuration File

Create a YAML configuration file to customize behavior:

```yaml
docroot: "~/.config/mcp-server-guide/docs"

projects:
  my-project:
    categories:
      guide:
        dir: "guide/"
        patterns:
          - "*.md"
        description: "General development guidelines"
      lang:
        dir: "lang/"
        patterns:
          - "*.md"
        description: "Language-specific guidelines"

    collections:
      backend:
        categories:
          - "api"
          - "database"
          - "auth"
        description: "Backend development resources"
```

### Default Categories

The following default categories are created when a project is first instantiated:

- **guide**: General developer guidelines (TDD methodology, coding standards, workflow requirements)
- **lang**: Programming language-specific guidelines (syntax, best practices, tooling, project structure)
- **context**: Project-specific information (issue management, specifications, workflow details)
- **prompt**: AI prompts shown by various built-in `@guide` commands

These are all regular categories that can be customized, removed, or renamed like any other category through the management functions. The `prompt` category is special in that it is checked for files corresponding to `@guide` commands; otherwise, built-in defaults are used.

## Examples & Workflows

### Setting Up a New Project

1. **Install and configure** the MCP server in your AI client
2. **Initialize categories** for your project:
   ```
   @guide category add --name "api" --dir "src/api/" --patterns "*.js,*.ts"
   @guide category add --name "tests" --dir "tests/" --patterns "*.test.js"
   ```
3. **Create collections** for logical grouping:
   ```
   @guide collection add --name "backend" --categories "api,database"
   ```
4. **Add project-specific documentation**:
   ```
   @guide document add --category "context" --name "setup" --content "# Project Setup Instructions"
   ```

### Development Workflow

1. **Start with guidelines**: `@guide guide` to understand project specifics
2. **Get language settings**: `@guide lang python` for Python-specific best practices
3. **Project context**: `@guide context` to understand project specifics

Or, you can group all three into a single collection and provide them all with `@guide <collection>`.

4. **Use phase commands** for structured development:
   - `@guide discuss "new feature implementation"`
   - `@guide plan "user authentication system"`
   - `@guide implement` (after planning approval)
   - `@guide check` (for validation and review)


### Managing Documentation

1. **Regular updates**: Keep categories and documents current with your project
2. **Use collections**: Group related categories for efficient access
3. **Leverage AI assistance**: Ask the AI to help manage your documentation structure
4. **Pattern vs managed**: Use patterns for dynamic content, managed documents for stable references

## Docker Deployment

For containerized deployments, Docker images are available:

```bash
# Production container (minimal footprint)
docker compose up mcp-server-guide-prod
```

### Environment Variables

- `MCP_LOG_LEVEL`: Set log level (default: `info` for prod, `debug` for dev)

For detailed Docker configuration, inspect the `Dockerfile.dev` and `Dockerfile.prod` files in the repository.

For technical documentation and API details, see [API.md](API.md).
