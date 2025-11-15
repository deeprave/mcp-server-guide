# MCP Guide Server API Reference

This document provides technical documentation for developers and AI agents working with the MCP Guide Server.

## Tool Prefix Behavior

- **Amazon Q** does not automatically namespace MCP tools, so the `guide_` prefix prevents name collisions with other MCP servers
- **Claude Code** automatically namespaces tools by server name, so the prefix is redundant and can be removed by setting `GUIDE_TOOL_PREFIX=""`
- Other clients may have different behaviors - adjust the prefix accordingly

## MCP Tools

### Core Tools

#### `guide_get_guide(category_or_collection, document)`

Retrieve guide content for a specific document in a category or collection.

**Parameters:**

- `category_or_collection` (string): Name of the category or collection to search
- `document` (string): Name of the document to retrieve

**Returns:** String content of the document, or `None` if not found

**Examples:**

```python
# Get a specific document from the 'guide' category
content = await guide_get_guide("guide", "guidelines")

# Get language-specific guidelines
content = await guide_get_guide("lang", "python")

# Get project context information
content = await guide_get_guide("context", "project-context")
```

#### `guide_list_categories()`

List all available categories in the current project.

**Returns:** List of category names

#### `guide_list_collections()`

List all available collections in the current project.

**Returns:** List of collection names

#### `guide_search_content(query)`

Search across all categories for content matching the query.

**Parameters:**

- `query` (string): Search query string

**Returns:** Search results with matching content

### Management Tools

#### Category Management

- `guide_add_category(name, dir, patterns, description=None)`
- `guide_update_category(name, **kwargs)`
- `guide_remove_category(name)`
- `guide_get_category_content(name, file=None)`

#### Collection Management

- `guide_add_collection(name, categories, description=None)`
- `guide_update_collection(name, **kwargs)`
- `guide_remove_collection(name)`
- `guide_get_collection_content(name)`

#### Document Management

- `guide_create_mcp_document(category_dir, name, content, mime_type=None)`
- `guide_update_mcp_document(category_dir, name, content)`
- `guide_delete_mcp_document(category_dir, name)`
- `guide_list_mcp_documents(category_dir)`

### Configuration Tools

- `guide_get_project_config()`
- `guide_set_project_config(config_key, value)`
- `guide_switch_project(name)`

## Prompts

### `@guide` Prompt Interface

The `@guide` prompt is the primary interface for accessing documentation, managing configuration, and controlling development workflow.

**Basic Usage:**

```
@guide help              # Show detailed help information
@guide category_name     # Show content from a specific category
@guide collection_name   # Show content from a specific collection
```

**Phase Commands:**

```
@guide discuss "topic"   # Start discussion phase with context
@guide plan "feature"    # Start planning phase with task details
@guide implement         # Start implementation phase
@guide check            # Start check/validation phase
```

## Content Types

### Pattern-Based Content

- Files matched by category patterns (e.g., `*.md` files in category directories)
- Automatically discovered based on file patterns
- Changes when files are added/removed from directories

### Managed Documents

- Specific documents uploaded via document management tools
- Unaffected by pattern matching
- Can reference category/document names directly without requiring pattern matches
- Persistent until explicitly removed

## Collections & Category Concatenation

**Collections** group multiple categories together for convenient access:
- Create collections that combine related categories
- Access multiple categories with a single command
- Useful for organizing related documentation

**Category Concatenation** allows referencing multiple categories:
- Use comma-separated category names: `@guide api,database,auth`
- Combines content from all specified categories
- Maintains logical organization while providing comprehensive context

## Error Handling

All tools return structured responses with success/error status. Check the `success` field in responses before processing results.

## Environment Variables

- `GUIDE_TOOL_PREFIX`: Controls tool name prefixing (default: "guide_")
- `GUIDE_PROJECT_NAME`: Override default project detection
- `GUIDE_CONFIG_PATH`: Custom configuration file path
