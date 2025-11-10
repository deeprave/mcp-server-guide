# Development guidelines & instructions

These instructions must be followed during the iterative development cycle.

**Method:** TDD (Red-Green-Refactor) with agile planning
**Language:** AU/UK English in all code, comments, and documentation

## Development Process

### Requirements & Planning
- Gather requirements and create comprehensive step-by-step implementation plan.
  Use a `requirements` agent do do this, if you have one.
- Break work into smallest possible tasks/subtasks
- Always use task checklists
- Identify unknowns - **ASK QUESTIONS** DO NOT make assumptions
- Never make architecturally significant decisions - ASK THE USER FOR GUIDANCE.

### Implementation

**🚨 MANDATORY USER CONSENT REQUIREMENT:**
1. Create detailed implementation plan
2. **EXPLICITLY REQUEST** user review and confirmation
3. **WAIT FOR EXPLICIT CONSENT** before making ANY changes to the project
4. **NEVER BYPASS THIS STEP - NO EXCEPTIONS**

**Core Principles:**
- **TDD MANDATORY:** Always write a failing test before implementation
  There are rare exceptions: refactoring existing features, fixing tests, research
- Follow **SOLID principles**, use clean and well encapsulated architecture
- Use consistent naming conventions and code style
  Always follow the existing code style.
- Write self-documenting code.
  Minimise comments exceptL API docs, IDE bookmarks, complex logic or algorithms/

### Iterative Development

**Pre-Check**
- Run complete test suite first (ensure that all tests pass)

**Discussion**
- The user will provide a story about the current iteration.
- Provide your analysis, do your research via web_search and the codebase
- Raise concerns, request clarity, present options. This is IMPORTANT.
- Ensure that you understand the user's request completely.

**Planning**
- Create the implementation plan breaking the work down into small steps
- Ensure the plan contains a checklist that can be updated during development

**Implementation**
- Implement step-by-step per the plan, following a TDD workflow
    - Create a failing test that embodies expected behaviour
    - Mark changes to production code, just enough to make the tests pass
    - Refactor if required, clean up and test again to ensure tests pass
- Raise questions if decisions are required, and present options to the user.
- At the end of each phase:
    - Unless otherwise directed, provide the user with opportunity to review after each step
    - Check each item in the plan as each phase is completed
    - Simplify your code, ensure tests still pass

**Check**
- Run all tests to ensure that tests pass
- Add integration tests as required
    - **100% test pass rate required**
    - fix ALL failing tests, no warnings, no side-effects
- Maintain required coverage threshold, but not artificially

### Definition of Done
- At the completion of each phase or cycle (user's preference) ensure that:
   - All tests pass, no exceptions, no excuses
   - Resolve all linting and type checking issues.
       - resolve means RESOLVE, not suppress unless with specific user consent.
   - Ensure that code is formatted according to the project standard
     This may involve using a language specific formatting tool.
   - Ensure that any text file created or edited has a terminating newline

### Version Control
- **NEVER** do any of the following git operations:
  - `git add` or `git push` (without explicit request)
    The user must manage the composition of a commit
  - `git commit`
    In most cases, the user must sign their commits, which the agent cannot do
  - `git revert`, `git checkout`, `git reset`, `git restore`,
    `git rebase`, `git merge`, `git filter-branch`, `git stash`
    All of these are destructive to the working tree and are FORBIDDEN.
    If you wish to fix an error or restore removed code, you must do this manually
    or request the user's assistance. NO EXCEPTIONS
  - On request, generate a concise commit messages the describes functional changes in the git commit cache.
    Include issue references for tracker association

## Confirmation Required
You must confirm your understanding of guidelines before proceeding.
