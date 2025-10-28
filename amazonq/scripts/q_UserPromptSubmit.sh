#!/bin/zsh
echo "🚨 You are in consent mode"
if [[ ! -f ".consent" ]]; then
  if [[ -s .issue ]]; then
    echo "📋 You are in **PLANNING** phase:"
    echo " - Discuss the feature with the user"
    echo " - Gather requirements from the current project, use web searches if required"
  else
    echo "💬 You are in **DISCUSSION** phase:"
    echo " - Create detailed plan or feature specification with checklists"
    echo " - Follow TDD using the smallest possible steps for creating features"
    echo " - Request and WAIT for approval - **NO EXCEPTIONS**"
    echo " - Current issues: $(cat .issue)"
  fi
else
  if grep -q 'check' .consent; then
    echo "✅ You are in **CHECK** phase:"
    echo " - Carry out checks and ensure that acceptance criteria have been met"
    echo " - Once completed YOU MUST ASK FOR USER CONFIRMATION before transition back to DISCUSSION phase"
  else
    echo "👔 You are in **IMPLEMENTATION** phase"
    echo " - Proceed with implementation and architectural changes as planned"
    echo " - Once implementation has been fully completed according to the plan:"
    echo "   - write 'check' to .consent file to transition to CHECK phase"
    echo "   - commence testing, lint, formatting and other checks as the project requires"
  fi
fi
exit 0
