# Project Context Instructions

These are instructions related to context specific to this project.

**Project:** Repostats (replicates gstats structure)
**Approach:** Minimalist, YAGNI
**YouTrack MCP:** RS project

## Architecture
- Loosely coupled modules with clear API boundaries
- Shared structures defined **outside** modules
- Encapsulate: module APIs via dedicated "api" sub-modules only
- **No direct imports** of non-public interfaces between modules
- EXCEPTIONS: Common code and bin-only modules

## Workflow
- **CRITICAL:** Pause after creating implementation plan for user review
- Working directory: `.todo`
- Implementation plan: `<issue-id-or-summary>-plan.md` containing the task checklist
- Update plan as work progresses after phase completion
- ALWAYS ASK FOR USER REVIEW BEFORE IMPLEMENTATION
- ALWAYS ASK THE USER IF QUESTIONS ARISE RELATED TO ARCHITECTURE

## Testing & Quality
- **ALL TESTS MUST PASS** at start and end of every phase
- Resolve build warnings (avoid using `#[allow(dead_code)]`unless with user consent)
- Maintain required coverage

## YouTrack Issue Management

### States
**Unresolved:** Backlog, Open, Reopened, In Progress
**Blocked:** Blocked, Delayed
**Resolved:** Done, Canceled, Won't fix, Can't Reproduce, Duplicate, Won't Do, Obsolete

### MCP Syntax (Critical Fix)
Always use a JSON Payload:
**✅ CORRECT kwargs:** `{"description": "content"}`
**❌ WRONG:** `"description": "content"`

```
search_issues: args: "", kwargs: {"query": "project: RS #Unresolved"}
get_issue: args: "", kwargs: {"issue_id": "RS-302"}
create_issue: args: "", kwargs: {"project": "RS", "summary": "Title", "description": "content\nwith newlines"}
add_comment: args: "", kwargs: {"issue_id": "RS-14", "text": "comment"}
update_issue: args: "issue_id=RS-56", kwargs: {"description": "content"}
YouTrack uses markdown format in descriptions and comments

**Notes:**
- Use actual `\n` not `\\n` in JSON strings
- Cannot change State field via MCP yet - inform user for manual change
- **NEVER** make direct curl calls, EVER, unless to localhost

## Git Rules
- **NEVER** commit without explicit request
- Concise commit messages describing functional not code changes
- Include issue references as prefix for YouTrack association
- No file-level details in messages

## Coding Rules
- Minimalist approach - no "future" fields/structs
- Use the language specific formatting utility to keep code formatted correctly
