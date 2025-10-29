#!/bin/zsh
if [[ ! -f ".consent" ]]; then
  echo "🚨 YOU MUST NOT MAKE ANY CHANGES TO THIS PROJECT"
  if [[ -s .issue ]]; then
    echo "📋 You are in **PLANNING** phase:"
    echo " - Create detailed plan or feature specification with checklists"
    echo " - Follow TDD using the smallest possible steps for creating features"
    echo " - Current issues: $(cat .issue)"
    echo " - Before implementation, request and WAIT for approval - **NO EXCEPTIONS**"
  else
    echo "💬 You are in **DISCUSSION** phase:"
    echo " - Discuss the feature(s) to implement with the user"
    echo " - Gather requirements from the current project, use web searches if required"
  fi
else
  echo "✅ YOU MAY MAKE CHANGES TO THIS PROJECT"
  if grep -q 'check' .consent; then
    echo "✅ You are in **CHECK** phase:"
    echo " - Carry out checks and ensure that acceptance criteria have been met"
    echo " - NERVER create a test, class, function or variable that contains the word 'coverage'."
    echo "   That is strictly BANNED. Adopt a sensible, functional and meaningful naming convention for all tests."
    echo " - Once completed YOU MUST ASK FOR USER CONFIRMATION before transition to DISCUSSION phase"
  else
    echo "👔 You are in **IMPLEMENTATION** phase"
    echo " - Proceed with implementation and architectural changes as planned"
    echo " - Once implementation has been fully completed according to the plan:"
    echo "   - write 'check' to .consent file to transition to CHECK phase"
    echo "   - commence testing, lint, formatting and other checks as the project requires"
  fi
fi
exit 0
