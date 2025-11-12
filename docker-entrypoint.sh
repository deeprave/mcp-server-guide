#!/bin/sh
set -e

# Change to project directory
cd /home/mcp/mcp-server-guide

# Sync dependencies (ensures they're up to date)
uv sync 1>&2

# Start the MCP server with configurable log level
echo "🚀 Starting MCP server..." 1>&2
exec uv run mcp-server-guide --log-level "${MCP_LOG_LEVEL:-info}"
