#!/bin/zsh
cat <<EOF
🚨 You are in consent mode.

DISCUSSION and PLANNING phase required before changes can be made.
  💬 **DISCUSSION**:Detailed Analysis, Requirements Gathering, Architectural Decisions
  📋 **PLANNING**: Implementation Planning, Specifications and Checklists
**IMPORTANT**
EXPLICIT USER CONSENT is REQUIRED to transition from planning to IMPLEMENTATION

IMPLEMENTATION and CHECKS phase making and checking required/planned changes.
  👔 **IMPLEMENTATION**: Execution of detailed plans, update progress in checklists
  ✅ **CHECK**: Ensure ALL applicable post-implementation tools such as tests are run and all pass

EOF
exit 0
