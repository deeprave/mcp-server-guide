# Developer guidelines

**Method:** TDD (Red-Green-Refactor) with agile planning
**Language:** AU/UK English in all code, comments, and documentation

## Development Process

### Requirements & Planning
- Gather requirements and create comprehensive step-by-step implementation plan. Use a `requirements` agent do do this, if you have one.
- Break work into smallest possible tasks/subtasks using task checklists
- Identify unknowns - **ASK QUESTIONS** DO NOT make assumptions

### Implementation

**🚨 MANDATORY USER CONSENT REQUIREMENT:**
1. Create detailed implementation plan
2. **EXPLICITLY REQUEST** user review and confirmation
3. **WAIT FOR EXPLICIT CONSENT** before ANY changes
4. **NEVER BYPASS THIS STEP - NO EXCEPTIONS**
5. **NEVER REMOVE/DELETE/MODIFY CODE WITHOUT EXPLICIT USER CONSENT**

**Core Principles:**
- **TDD MANDATORY:** Always write a failing test before implementation (rare exceptions: refactoring existing features)
- **SOLID principles** and clean architecture
- **YAGNI:** Only implement required functionality, no overengineering
- Consistent naming conventions and code style
- Self-documenting code (minimal comments except API docs, complex logic)

### Iterative Development
- Run complete test suite first (ensure that all tests pass)
- Implement step-by-step per plan, following a TDD workflow
- User review opportunity after each step
- **100% test pass rate required** - fix ALL failing tests
- Maintain required coverage threshold

### Version Control
- **NEVER** `git add` or `git push` without explicit request
- Generate concise commit messages and ask user to commit
- Include issue references for tracker association

## Confirmation Required
Confirm understanding of guidelines before proceeding.
