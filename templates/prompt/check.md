**Instruction**: You have consent to transition to CHECK mode.

🔍 You are now in CHECK phase

🚨 **CHECK PHASE RULES**

- Verify checklists in task specification/implementation plan are complete
- Do NOT automatically transition to DISCUSSION until user confirms satisfactory completion
- No production code changes UNLESS fixing issues raised by check tooling
- Create new tests, formatting and fixing encouraged

**Quality Gate Requirements:**

- **ALL TESTS MUST PASS. EVERY TEST.**
- Meet/exceed targets, lint code, type-check, format to standard
- Ask user to specify focus: suggestions, bugs/logic errors, or feedback

**Instructions:**

- Do NOT remove `.issue` file until user declares task complete
- Do NOT remove `.consent` file until user explicitly enters discussion phase
- 100% test pass rate required - no warnings/errors
- Use proper naming conventions - describe what's being tested clearly
- Don't test removed features/failed imports
- Update specification/task documents marking completed items

**NEXT:** DISCUSSION phase (requires user confirmation and `.consent` file removal)
