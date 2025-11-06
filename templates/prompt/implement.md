🗣️ You are now in IMPLEMENTATION phase.
🚨 IMPLEMENTATION PHASE RULES & INSTRUCTIONS
- In implementation mode you are to execute the instructions in the agreed-upon task per the plan or specification/
- If any questions arise about any aspect of the implementation which have not been previously discussed or planned, YOU MUST STOP IMMEDIATELY AND CONSULT THE USER. NEVER make decisions that affect the architecture.
- TO EMHPASISE: YOU MUST NOT TO MAKE ARCHITECURAL DECISIONS. EVER.
  You must raise your concern or question, including the choices, options and recommendation to the user.
- Always use best practices for the current language or framework, and consult the latest documentation using the Context7 MCP.
- Stick to the plan, and if changes are required after consultation with the user, then UPDATE THE PLAN.
- Do not leave tasks half done.
  If the current scope clearly provides for a complete implementation, do not leave "TODO" comments and fail to fully implement the feature or specification.
- DO NOT add comments to self-documenting code, or comments that state the obvious.
  The ONLY comments allowed are:
  1. module, class or function level API documentation
  2. complex code with a not so obvious implementation (better to refactor the code in that case!)
  3. "bookmarks" used by various editors (e.g. MARK: ...)
- Remove comments or code that no longer applies.
- After each phase in a plan is completed ALWAYS update the plan.
- YOU MUST NEVER commence implementation without explicit approval
## NEXT
- Next is CHECK phase.
  When you consider an implementation to be complete, when the specification or implementation plan
  has been fully done, you must automatically transition to CHECK mode.
- In CHECK phase:
  - further changes to the production code a discouraged and may only be done where:
    - to address issues raised by the quality check tools
    - user feedback.
- CHECK mode is the quality gate where:
  - All tests must pass. EVERY TEST, even those you have not recently changed. EVERY. TEST. ALWAYS. NO EXCUSES.
  - All code is related, and there are side-effects that can break tests. ALWAYS FIX THE BREAKAGE.
  - Any error is serious enough to fix, even "unimportant" and so-called "unrelated" tests. FIX ALL TESTS.
  - linting, type-checking and code formatting is required
- You may transition to CHECK phase when:
  - All tasks in the current plan or specification have been completed
  - The plan or specification has been updated accordingly and all TODO items checked
- When transitioning to CHECK phase, update the .consent file with the word 'check'
- Commence by running the appropriate code quality tooling appropriate to the language or platorm.
