# Kiro-CLI Integration

Files in this directory are for integration with the Amazon Kiro CLI client.

## Prerequisites

- Kiro CLI installed and configured
- Access to the terminal/command line

## Quick Installation

1. Verify Kiro CLI installation:

   ```bash
   kiro-cli --version
   ```

2. Run the installation script:

   ```bash
   mcp-server-guide-kiro-install
   ```

   This script automatically installs the `guide` and `guide-review` agents along with required hook scripts to `~/.kiro/agents` and `~/.kiro/scripts`.

   **Note for existing users:** The agent names have been updated from `consent`/`review` to `guide`/`guide-review`. This reduces the likelihood of overwriting any custom agents you may have created, and the names clearly indicate their origin from mcp-server-guide.

3. Set `guide` as your default agent:

   ```bash
   kiro-cli settings chat.defaultAgent guide
   ```

   This will cause kiro-cli chat to display `[guide]` before each prompt to remind you that the agent is active.

6. Verify installation:

   ```bash
   kiro-cli chat
   ```

   You should see the `[guide]` prompt indicating the agent is active.

7. When in CHECK mode, the guide agent will now pause once completed and before returning
   to DISCUSSION mode. This is an ideal time to switch to guide-review mode:

   ```shell
   /agent swap guide-review
   ```

   and simply ask it to review.

   Review mode is a "read-only" mode that allows the agent to do a deep review and create a
   markdown file with issues: critical, warning and notes (optionals).
   To switch back to the guide agent:

   ```shell
   /agent swap guide
   ```

## Troubleshooting

- If `kiro-cli chat` doesn't show `[guide]`, verify the agent was set correctly:
  `kiro-cli settings chat.defaultAgent`
- If scripts fail to execute, ensure they have proper permissions:
  `ls -la ~/.kiro/scripts/*`

## DISCUSSION & PLANNING Phases

This is a "close enough" implementation of **DAIC** (Discussion-Alignment-Implementation-Check) for Kiro-cli,
born from the concept introduced in [cc-sessions](https://github.com/GWUDCAP/cc-sessions).
Claude Code's hooks make enforcement of DISCUSSION and PLANNING phases of the development cycle much
simpler and more deterministic, but Kiro-cli lacks the same level of sophistication to fully support
this functionality.
mcp-server-guide fills that gap by providing guardrails based on instructing the agent to do the right thing.
This is surprisingly successful.

The DAIC concept is blended the GitHub spec-kit has also been done (work is in progressfor a more complete
integration), introducing an additional subphase of DISCUSSION mode, called "PLANNING" (`plan` prompt).
This is a phase where the agent is asked to create a plan, (saved as markdown) for the implementation work
about to be undertaken.

Similarly, a CHECK phase is also being introduced as a subphase of IMPLEMENTATION mode, where the agent
is asked to check the implementation work against the plan using the usual check tools for the current
project (type checks, linting, unit and integration tests, etc.).

An additional guide-review agent is also provided in this repository.
Its use is optional, however, my personal experience is that this offers a lot of value that supplements
the code review process.

With Kiro-CLI, an agent needs to be used with some accompanying scripts to fully support DISCUSSION
and PLANNING phase enforcement.
However, the same idea should work with most agentic clients, although the implementation details will differ.

With this MCP, DISCUSSION mode is the default state.
An agent should be prevented from doing any implementation work until the file ".consent" appears at
the project root.
Sub-phases of DISCUSSION mode are indicated (but not strictly enforced) by the presence of a non-empty
.issue file.
The .issue file is used to keep track of the current issue being planned or implemented,
and the agent should be instructed to write the path to the plan or specification document during
the planning phase.

The sp_reToolUse.sh script includes some exceptions that are intended to allow the agent write access
to specific folders for creating and updating implementation plans or specifications.
It will also allow a subset of shell commands to be executed that do not cause changes to the project
outside of the folder dedicated to plans and specifications.

The prompts `@guide :discuss` and `@guide :implement` provide a means to manually switch modes,
and `@guide :status` asks the agent to provide the current status.
Alternatively, asking the agent to switch mode and providing consent when requested will usually
trigger it to do the correct thing.

Handling of the .consent and .issue file is done by instructing the agent as the MCP is unable nor
required to have filesystem access.

## Agents

Using this MCP requires an agent so that it can be configured with custom commands and permissions
that do not interrupt the workflow.

The `guide.json` file in the agents directory is a fully working example configuration for
Kiro-CLI agents that enables enforcement of DISCUSSION functionality (restricted filesystem operations)
through hook scripts.

Similarly, `guide-review.json` sets the schene for the agent to review its own work, critically and analytically,
to hopefully clean up after its most common failings - code duplication, inconsistent implementation
(different sessions!), over-engineering and simple lapses of which even we humans are all guilty from time to time.

