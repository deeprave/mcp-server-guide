# DAIC Compliance Rules

## Purpose

Enforce DAIC - Discussion-Alignment-Implementation-Check workflow

## Description

DAIC is a four step structure workflow for development of software using an agentic AI.

### Discussion
This step involves a discussion betewen the Developer and the AI Agent, exchanging ideas, clarifying and covering, amongst other things, the following topics.
This step in the cycle is concerned with:
  - Defining the objective
  - Recognising the pre-requisites and requirements, both functional and non-functional
  - Being clear about assumptions being made
  - Gathering and documenting context
  - Clarifying the scope

### Alignment
This is where the Developer and the AI Agent come to an agreement about the work to be confirmed, the form it takes and the designs involment.

Alignment usually takes the form of a a detailed implementation plan or specification.

Plans can - and should - be broken down into the smallest functional and testable parts.

> **IMPORTANT**
>
> In these first two steps no work is done (as in, no code added, removed or refactored).
> The AI Agent is explicitly blocked from writing and updating the codebase, but may create and edit plans specifications and diagrams, usually in markdown format.
> The AI is allowed to search and read the code and can bring in additional context from web searches or other documentation.
> But it MUST wait for Developer's consent and agreement with the plan before continuing.

### Implementation

In this section, the AI Agent has detailed knowledge on the work to be performed and will do so in a step by step fashion according to the agreed plan.
It must implement all that has been planned, no more and no less.
It must adhere closely to the plan, but should be free to invite the Developer's direction or comment at any point during the implementation for any reason.
It MUST invite comments and decisions for anything that is not mentionede in the plan and previously agreed upon.

### Check

Once the impelementation has been completed, this workflow enters the "check" phase.
This is where the Developer must provide feedback on the implementation, and the AI agent is allow to plan and execute revisions based on that feedback.

A check phase may fall back into Discussion mode, and should do so by default.
However the check -> dicussion -> implementation cycle may repeat multiple time until the implementation is accepted by the Developer.

Once all checks have been completed, and all issues in the Developer's feedback have been enacted, the cycle immediately returns to Discussion mode.

## Instructions

- NEVER generate implementation code without explicit user approval of the plan (ID: DISCUSSION)

- If the user brings up a topic, asks for clarification, poses a question, or interrupts the implementation you are automatically in Discussion mode and MUST NOT IMPLEMENT without consent.

- ALWAYS first present a detailed implementation plan (ID: ALIGNMENT) including:
  * Files to be modified
  * Key changes to be made
  * Potential risks or impacts

- ALWAYS wait for explicit confirmation before making any code changes (ID: CONSENT)

- ALWAYS implement exactly as stated in the plan - no more and no less (ID: IMPLEMENTATION)

## Completing Implementation

- When you complete an implementation and return to the user prompt:
  - Summarize the changes made
  - Enter Discussion mode - NOT MORE CHANGES WITHOUT APPROVAL (ID: CONSENT)
  - Wait for the Developer feedback (ID: CHECK)

- During the check phase, you may have to implement and discuss in quick succession several times based on the Developer's feedback. No additions to the scope hould be considered at this time.

## Priority

CRITICAL
