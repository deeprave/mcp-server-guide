🗣️ You are now in PLAN phase.
🚨 PLAN PHASE RULES
- You may not create, edit or remove files.
- **Exceptions**:
  - discussion briefs, specifications, implementation plans and checklists
  - you may remove the .consent file if it exists
  - you may create, remove or update the issue .issue at the user's instruction
  - you must add the implementation plan path(s) to the .issue file when they are created
## Instructions for PLANNING phase
- Plan mode is for deciding HOW an implementation is to be done.
- Plans must consist of todo items broken down into the smallest possible testable units
- Except for specific circumstnaces where not possible, ALWAYS used a proper TDD approach
  - break large tasks into small testable units.
  - write failing tests first, make them pass with the minimum amount of changes
  - then refactor if require
  - do not create separate tasks for red-green-refactor tests, all 3 combined is 1 single task
- YOU MUST NOT START implementation without EXPLICIT APPROVAL
## NEXT
- Before entering the next phase IMPLEMEMENTATION - you MUST request the user's explicit consent.
- Ensure the `.issue` file contains the path to the created task(s):
  - The immediate specification or implementation plan must be on the first line in the `.issue` file
- When transitioning into IMPLEMENTATION mode you are to create the .consent file contining
  the word 'implementation'
