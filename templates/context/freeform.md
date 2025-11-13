# Project Context Instructions

These are instructions related to context specific to this project.

**Project:** Generic
**Approach:** Minimalist, YAGNI*
**Issue Management**: Local

## Workflow

- **CRITICAL:** Pause after creating implementation plan for user review
- Working directories:
  - `.todo`        - work items
  - '.todo/done'   - completed items
  - '.adr'         - architecture decision records
- Append plans to the .issue file when created, or prepend them high-priority issues.
- By default, one or more of these files:
    - <issue-id>-<short summary>-spec.md       - WHAT: specification, description, requirements, goals
    - <issue-id>-<short summary>-plan.md       - HOW: detailed implementation plan
    - <issue-id>-<short summary>-tasks.md      - Detail: checklist, TDD flow
- Update tasks file checklists as work is completed
- ALWAYS ASK THE USER IF QUESTIONS ARISE RELATED TO ARCHITECTURE
- ALWAYS ASK FOR USER REVIEW BEFORE IMPLEMENTATION

## Testing & Quality

- **ALL TESTS MUST PASS** and **WITHOUT WARNINGS** at start and end of each plan
- Resolve build warnings any means of suppressing them
- Exceptions to these rules (other than 100% pass rate for tests without warnings)
  can be made after the user has provided explicit and specific consent.
