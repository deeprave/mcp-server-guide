# Architecture

This document describes the technical architecture and implementation details of the MCP Rules Server.

## 🏗️ **System Architecture**

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

# Saves to .mcp-server-guide.config.json in project root
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

## **Configuration Precedence**

Configuration values are resolved in the following order (highest to lowest priority):

1. **CLI Arguments** - Explicitly provided command line options
2. **Environment Variables** - Environment variables with `MCP_` prefix
3. **Persistent Configuration** - `.mcp-server-guide.config.json` files
4. **Session Overrides** - Runtime session modifications
5. **Defaults** - Built-in default values

## **File Source Types**

### **Local Files (`local:`)**
- Accesses files on the client filesystem
- Direct file system operations
- No caching required

### **Server Files (`server:`)**
- Accesses files on the server filesystem
- Direct file system operations
- No caching required

### **HTTP Resources (`https:`)**
- Fetches files from remote HTTP servers
- HTTP-aware caching with validation headers
- Conditional requests (If-Modified-Since, If-None-Match)
- Network error fallback to cached content

### **Context-Aware Files (`file://`)**
- Automatically detects deployment context
- Routes to local or server based on environment
- Seamless switching between development and production

## **HTTP Caching System**

### **Cache Validation**
- Uses `Last-Modified` and `ETag` headers for validation
- Respects `Cache-Control` directives
- Makes conditional requests to minimize bandwidth
- Falls back to cached content on network errors

### **Cache Storage**
- JSON-based persistent cache files
- SHA256 hashing for cache keys
- Configurable cache directory and size limits
- Automatic cleanup of expired entries

## **Project Configuration**

### **Configuration Files**
- `.mcp-server-guide.config.json` in project root
- JSON format with structured data
- Automatic project root detection
- Real-time file watching for changes

### **Configuration Schema**
```json
{
  "project": "string",
  "guide": "string (URL or path)",
  "language": "string",
  "docroot": "string (path)",
  "guidesdir": "string (path)",
  "langdir": "string (path)",
  "projdir": "string (path)",
  "tools": ["array", "of", "strings"]
}
```

## **Session State Management**

### **Session Persistence**
- Singleton SessionManager pattern
- In-memory session state with project switching
- Integration with persistent configuration
- Effective configuration merging

### **Project Context**
- Automatic project detection from directory structure
- Context-aware file path resolution
- Session-specific configuration overrides

## **Development**

### **Testing Strategy**
- Test-Driven Development (TDD) approach
- Unit tests for individual components
- Integration tests for system interactions
- 93% test coverage across all modules

### **Code Quality**
- Type hints throughout codebase
- Linting with ruff
- Formatting with ruff
- Pre-commit hooks for quality assurance

### **Module Structure**
```
src/mcp_server_-_guide/
├── __init__.py
├── config.py              # CLI configuration
├── file_cache.py          # HTTP caching system
├── file_source.py         # File source abstraction
├── http_client.py         # HTTP client with conditional requests
├── project_config.py      # Persistent configuration
├── server.py              # MCP server implementation
├── session.py             # Session path resolution
├── session_tools.py       # Session management
└── session_tools.py       # Session utilities
```
