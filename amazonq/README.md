# AmazonQ Integration

Files in this directory are for integration with the AmazonQ client.

## Prerequisites

- Amazon Q CLI installed and configured
- Access to terminal/command line

## Quick Installation

1. Verify Q CLI installation:
   ```bash
   q --version
   ```

2. Create directories if they don't exist:
   ```bash
   mkdir -p ~/.aws/amazonq/cli-clients ~/.aws/amazonq/scripts
   ```

3. Copy the consent agent to your AmazonQ cli-clients directory:
   ```bash
   cp -v cli-clients/consent.json ~/.aws/amazonq/cli-clients/consent.json
   ```

4. Copy the content of scripts folder to the `scripts` subdir and set permissions:
   ```bash
   cp -rv scripts/* ~/.aws/amazonq/scripts/
   chmod +x ~/.aws/amazonq/scripts/*.sh
   ```
   Note: The location of these scripts is unimportant, so if you wish to place them elsewhere you may do so, but the paths in the consent.json will need to be adjusted.

5. Make `consent` your default cli agent with the following command:
   ```bash
   q settings chat.defaultAgent consent
   ```
   This will cause q chat to display `[consent]` before each prompt to remind you that the agent is active.

6. Verify installation:
   ```bash
   q chat
   ```
   You should see the `[consent]` prompt indicating the agent is active.


## Troubleshooting

- If `q chat` doesn't show `[consent]`, verify the agent was set correctly: `q settings chat.defaultAgent`
- If scripts fail to execute, ensure they have proper permissions: `ls -la ~/.aws/amazonq/scripts/`
- If directories don't exist, create them manually: `mkdir -p ~/.aws/amazonq/cli-clients ~/.aws/amazonq/scripts`

## DAIC Mode

This is a "close enough" implementation of **DAIC** (Discussion-Alignment-Implementation-Check) for Amazon Q, born from the concept introduced in [cc-sessions](https://github.com/GWUDCAP/cc-sessions). Claude Code's hooks make enforcement of DAIC mode much simpler and more deterministic, but Q lacks the same level of functionality.

Instead, an agent needs to be used with some accompanying scripts to fully support DAIC enforcement. However the same idea should work with most agentic clients, although the implementation details may differ.

With this MCP, the enabled DAIC mode is the default state. An agent should be prevented from doing any implementation work until the file ".consent" appears at the project root.

The q_PreToolUse.sh script includes a couple of exceptions that are intended to allow the agent write access to specific folders for creating and updating implementation plans or specifications.

The mcp-server-guide prompts `@daic on` and `@daic off` provide a means to manually switch modes, and `@daic` without arguments returns the current state. In claude code, this can be

## Agents

Using this MCP requires an agent so that it can be configured with custom commands. The "consent.json" file in this directory is an example configuration for Amazon Q CLI agents that enables DAIC functionality through hook scripts.
