# AmazonQ Integration

Files in this directory are for integration with the AmazonQ client.

## Prerequisites

- Amazon Q CLI installed and configured
- Access to the terminal/command line

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
   cp -rv cli-clients/ ~/.aws/amazonq/cli-clients/
   ```
4. Copy the content of scripts folder to the `scripts` subdir and set permissions:

   ```bash
   cp -rv scripts/* ~/.aws/amazonq/scripts/
   chmod +x ~/.aws/amazonq/scripts/*/*.sh
   ```

   Note: The location of these scripts is unimportant, so if you wish to place them elsewhere you may do so, but the paths in the agent files `consent.json` and `review.json` will need to be adjusted.
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
7. When in CHECK mode, the consent agent will now pause once completed and before returning to DISCUSSION mode. This is an ideal time to switch to consent mode:

   ```shell
   /agent swap review
   ```

   and simply ask it to review.

   Review mode is a "read-only" mode that allows the agent to do a deep review and create a markdown option with issues: critical, warning and notes (optionals). To switch back to the consent agent:

   ```shell
   /agent swap consent
   ```

## Troubleshooting

- If `q chat` doesn't show `[consent]`, verify the agent was set correctly: `q settings chat.defaultAgent`
- If scripts fail to execute, ensure they have proper permissions: `ls -la ~/.aws/amazonq/scripts/`
- If directories don't exist, create them manually: `mkdir -p ~/.aws/amazonq/cli-clients ~/.aws/amazonq/scripts`

## DISCUSSION & PLANNING Phases

This is a "close enough" implementation of **DAIC** (Discussion-Alignment-Implementation-Check) for Amazon Q, born from the concept introduced in [cc-sessions](https://github.com/GWUDCAP/cc-sessions). Claude Code's hooks make enforcement of DISCUSSION and PLANNING phases of the development cycle much simpler and more deterministic, but Q lacks the same level of sophistication to fully support this functionality. mcp-server-guide fills that gap by providing guardrails based on instructing the agent to do the right thing. This is surprisingly successful.

The DAIC concept is blended the GitHub spec-kit has also been done (work is in progressfor a more complete integration), introducing an additional subphase of DISCUSSION mode, called "PLANNING" (`plan` prompt). This is a phase where the agent is asked to create a plan, (saved as markdown) for the implementation work about to be undertaken.

Similarly, a CHECK phase is also being introduced as a subphase of IMPLEMENTATION mode, where the agent is asked to check the implementation work against the plan using the usual check tools for the current project (type checks, linting, unit and integration tests, etc.).

An additional review agent is also provided in this repository. Its use is optional, however, my personal experience is that this offers a lot of value that supplements the code review process.

In Amazon Q, an agent needs to be used with some accompanying scripts to fully support DISCUSSION and PLANNING phase enforcement. However, the same idea should work with most agentic clients, although the implementation details will differ.

With this MCP, DISCUSSION mode is the default state. An agent should be prevented from doing any implementation work until the file ".consent" appears at the project root.
Sub-phases of DISCUSSION mode are indicated (but not strictly enforced) by the presence of a non-empty .issue file.
The .issue file is used to keep track of the current issue being planned or implemented, and the agent should be instructed to write the path to the plan or specification document during the planning phase.

The q_PreToolUse.sh script includes some exceptions that are intended to allow the agent write access to specific folders for creating and updating implementation plans or specifications.  It will also allow a subset of shell commands to be executed that do not cause changes to the project outside of the folder dedicated to plans and specifications.

The prompts `@discuss` and `@implement` provide a means to manually switch modes, and `@status` asks the agent to provide the current status.

Handling of the .consent and .issue file is done by instructing the agent as the MCP is unable nor required to have filesystem access.

## Agents

Using this MCP requires an agent so that it can be configured with custom commands and permissions that do not interrupt the workflow. The `consent.json` file in the cli-agents directory is a fully working example configuration for Amazon Q CLI agents that enables enforcement of DISCUSSION functionality (restricted filesystem operations) through hook scripts.

Similarly, `review.json` sets the schene for the agent to review its own work, critically and analytically, to hopefully clean up after its most common failings - code duplication, inconsistent implementation (different sessions!), over-engineering and simple lapses of which we are all guilty from time to time.

