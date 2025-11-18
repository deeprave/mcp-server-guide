# MCP Server Guide - Installation Guide

After installing `mcp-server-guide` from PyPI, you need to set up the template files and configuration to point to them. The package includes a script to do this and installs an executable mcp-server-guide-install.

## Prerequisites

### System Dependencies

The server requires `libmagic` for content-based file type detection:

**macOS:**
```bash
brew install libmagic
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libmagic1
```

**Fedora/RHEL:**
```bash
sudo dnf install file-libs
```

**Windows:**
```bash
# Install via chocolatey
choco install file
```

## Quick Start

### 1. Install the Package

```bash
pip install mcp-server-guide
```

```bash
uv tool install mcp-server-guide
```

Unfortunately you need to install this once in order to run the installation script, but you can remove it after and use uvx instead from your mcp configuration to ensure that you are downloading and using the latest release.

### 2. Run the Installation Command

```bash
mcp-server-guide-install
```

This (optoionally interactive) command will:
- Prompt you for where to install template files (with a sensible default)
- Copy templates from the package to your chosen location
- Create the mcp server configuration at `~/.config/mcp-server-guide/config.yaml`
- Set the `docroot` in that configuration to point to the location where you isntalled the templates.

Note that these templates can and _should_ be edited by you to suite your development style.
The default setup mandates a TDD development style, which some may not want.
Regardless, the Discuss -> Plan -> Implement -> Check development cycle is Guide's natural flow.
With some judicious editing of prompts and instructions, you can devise any alternative that you may prefer.

### 3. Start the Server

The server is started with the command:
```bash
mcp-server-guide
```
This would normally be configured as an agent MCP. It runs in stdio by default.
The typical json configuration would look something like:

```json
    "Guide": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "mcp-server-guide",
        "stdio"
      ]
    },
```

## Advanced Installation

### Custom Installation Path

To specify a custom installation path without interactive prompts:

```bash
mcp-server-guide-install --path /custom/path/to/templates
```

Or shorter form:
```bash
mcp-server-guide-install -p /custom/path/to/templates
```

### Configuration File

After installation, your configuration on unix-like systems is stored at:

### Linux/macOS
```
~/.config/mcp-server-guide/config.yaml
```
### Windows
```
%APPDATA%\mcp-server-guide
```

There is a `--config` or `-c` command line switch to use a different location should you prefer.
The one configuration file configures as many projects as you wish, and as many agents that you use.

The initial configuration file contains:
```yaml
docroot: /path/to/your/templates
```

You can edit this file to change the template location, or re-run the installer.
It is not recommended to change other configuration items that the server will create here,
and other than the docroot all other settings can be directly managed from the agent.

The installer does not overwrite existing templates or configuration files, but does alter the docroot.

If you run this MCP server under docker, the documents are managed within the docker container, but you can and should use a data volume for these files to ensure they persist over restarts (and therefore retain your edits).
The _docroot_ path in that case would be a directory or mount point within the container.
A host mounted directory works well if you wish to customise and augment these files.

## Typical Installation Locations

The installer defaults to one of these locations based on your operating system:

- **Linux/macOS**: `~/.local/share/mcp-server-guide/templates`
- **Windows**: `%APPDATA%\mcp-server-guide\templates`

You can change this during installation if desired.

## Troubleshooting

## Uninstallation

To completely remove the application:

```bash
# Remove the package
pip uninstall mcp-server-guide
# or uv tool uninstall mcp-server-guide

# Optionally remove templates (keep config as reference)
rm -rf ~/.local/share/mcp-server-guide/

# Optionally remove configuration
rm -rf ~/.config/mcp-server-guide/
```

## Support

For issues or questions:
- Check the project repository
- Review the configuration file: `~/.config/mcp-server-guide/config.yaml`
- Run the installer again to reconfigure
