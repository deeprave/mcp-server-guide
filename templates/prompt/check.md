🗣️ You are now in CHECK mode.

🚨 CHECK MODE RULES
- At the completion of IMPLEMENTATION mode when planned changes are considered complete,
  ensure that checklists in the task specification or implementation plan has been checked
  and inform the user of your status.
- Do not automatically transition to DISCUSS mode until the user confirms that all work is
  completed to a satisfactory standard
- No further changes should be done the production code must be done UNLESS to fix an issue
  raised by the check tooling.
- You are allowed and encouraged to create new tests and do anything related to testing,
  formatting and fixing.
- CHECK mode is the quality gate where the requirements are:
  - ALL TESTS MUST PASS. EVERY TEST, not just those recently touched. EVERY. TEST.
  - Coverage targets must be met and, where possible, exceeded.
  - all code is appropriatedly linted (see language tooling)
  - type-checking (again, language specific tooling)
  - code formatted to standard
- Before running the quality gate checks, ask the user to specify whether they want to
  focus on suggestions, find bugs and logic errors or address feedback.
### Instructions
- Do not remove the .issue file the task/implementation plan is checked and declared BY THE USER
  the user to be completed.
- Do not remove the .consent file until the user explicitly enters discussion mode or declares
  the current issue as completed.
- Less than 100% pass rate for the entire suite of tests is unacceptable.
- The test must run without warnings or errors.
- Never use the word "coverage" in file, class, module names or mention coverage or coverage%
  in comments or function names. USE PROPER NAMING CONVENTIONS. ALWAYS. Names assigned should describe
  clearly what is being tested - unambiguously and clearly - that is the purpose of testing, not to
  achieve an abitrary "coverage" percentage.
- Do not "test" that a remmoved feature, function, block of code is absent, or an import fails and
  the similar. If something is no longer in the codebase IT IS NOT WORTH TESTING.
- If there is a specification, task or implementation document, always update it and mark items
  that have been done as completed.
## NEXT
- Next, we return to DISCUSS mode.
- After user confirmation, when transitioning to DISCUSS mode, you MUST remove the .consent file.
