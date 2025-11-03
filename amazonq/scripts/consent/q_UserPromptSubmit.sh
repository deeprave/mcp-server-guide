#!/bin/bash
if [[ ! -f ".consent" ]]; then
  echo "🚨 You MUST NOT make changes to the project"
  echo " - You MAY create plans, specifications and tasks within the agreed upon folder"
  if [[ -f .issue ]]; then
    echo "📋 You are in **PLANNING** phase:"
    echo " - Current issues: $(cat .issue)"
    echo " - When planning concludes ensure that the implementation plan is written to disk: console memory is too short"
    echo "   - If the task allows (almost always!) draft TDD red-green-refactor with smallest possible steps"
    echo "   - Plans and specifications must include a checklist"
    echo " ▶ Transition"
    echo " - Before implementation, request and WAIT for approval - **NO EXCEPTIONS**"
  else
    echo "💬 You are in **DISCUSSION** phase:"
    echo " - Discuss the feature(s) to implement with the user"
    echo " - Gather requirements from the current project, use web searches if required"
    echo " ▶ Transition"
    echo " - When aligned with the user and all questions answered, you may move into planning mode"
    echo " - If it does not already exist, create the .issue file"
  fi
else
  echo "😎 You may make changes to the project"
  if grep -q 'check' .consent; then
    echo "✅ You are in **CHECK** phase:"
    echo " - Carry out checks and ensure that acceptance criteria have been met"
    echo " - NEVER create a test, class, function or variable that contains the word 'coverage'."
    echo " - Once tests pass, ensure that post commit code quality tasks have been done"
    echo " - The user may provide feedback which may involve additional fixes and changes"
    echo " ▶ Transition"
    echo " - Before returning to DISCUSSION phase, request and WAIT for approval - **NO EXCEPTIONS**"
  else
    echo "👔 You are in **IMPLEMENTATION** phase"
    echo " - Proceed with implementation and architectural changes as planned"
    echo " - As tasks and phases are completed, ensure that then plan or specification is updated accordingly"
    echo " - At the end of each phase **ALWAYS** run the full test suite"
    echo "     - Always fix test errors and warnings, even if you think them unrelated to current work"
    echo " ▶ Transition"
    echo " - Once implementation has been fully completed according to the plan.."
    echo "   - write 'check' to .consent file to transition to CHECK phase"
    echo "   - commence testing, lint, formatting and other checks as the project requires"
  fi
fi
exit 0
