# AmazonQ Integration

Files in this directory are for integration with the AmazonQ client.

## Quick Installation

1. Copy the consent agent to your AmazonQ cli-clients directory:
   `cp -v cli-clients/consent.json ~/.aws/amazonq/cli-clients/consent.json`
2. Copy the content of scripts folder to the `scripts` subdir (creating of it does not already exist).
   `cp -rv scripts ~/.aws/amazonq`
   The location of these scripts is unimportant, so if you wish to place them elsewhere you may do so, but the paths in the consent.json will need to be adjusted
1. Make `consent` your default cli agent with the following command:
   `q settings chat.defaultAgent consent`
   This will cause q chat to display `[consent]` before each prompt to remind you that the agent is active.


## DAIC Mode

This is a "close enough" implementation of **DAIC** (Discussion-Alignment-Implementation-Check) for Amazon Q, born from the concept introduced in [cc-sessions](https://github.com/GWUDCAP/cc-sessions). Claude Code's hooks make enforcement of DAIC mode much simpler, but Q lacks the same functionality.

Instead, an agent needs to be used with some accompanying scripts to fully support DAIC enforcement. However the same idea should work with most agentic clients, although the implementation may differ.

With this MCP, the enabled DIAC mode is the default state. An agent should be prevented from doing any implementation work until the file ".consent" appears at the project root.

The prompts `@daic on` and `@daic off` provide a means to manually switch modes, and `@daic` without arguments returns the current state.

## Agents

Using this MCP requires an agent so that it can be configured with custom commands. The "consent.json" file in this directory is an example configuration for the [Auto-GPT](
