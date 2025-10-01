# DAIC Compliance Rule

## Purpose

Enforce Discussion-Alignment-Implementation-Check workflow

## Instructions

- NEVER generate implementation code without explicit user approval of the plan (ID: DAIC_APPROVAL)
- If the user brings up a topic or asks a question, you are automatically in DAIC mode and MUST NOT IMPLEMENT without consent.
- ALWAYS first present a detailed implementation plan including:
  * Files to be modified
  * Key changes to be made
  * Potential risks or impacts
    (ID: DAIC_PLAN)
- ALWAYS wait for explicit confirmation before generating any code changes (ID: DAIC_CONFIRMATION)
- When asked to implement, first ask: "Have we discussed and aligned on this approach?" (ID: DAIC_CHECK)

## After Implementation

- When you complete an implementation and return to the user prompt:
  - Summarize the changes made
  - Enter DAIC mode - NOT MORE CHANGES WITHOUT APPROVAL (ID: DAIC_APPROVAL)

## Priority

CRITICAL
