#!/bin/bash
cat <<EOF
🚨 You are in guided mode.

DISCUSSION and PLANNING phases are required before implementation.
  💬 **DISCUSSION**: Detailed Analysis, Requirements Gathering, Architectural Decisions, Creating Specifications
  📋 **PLANNING**: Implementation Planning and Task Checklists

IMPLEMENTATION and CHECKS phase making and checking required/planned changes.
  👔 **IMPLEMENTATION**: Execution of detailed plans, update progress in checklists
  ✅ **CHECK**: Ensure ALL applicable post-implementation tools such as tests are run and all pass

**IMPORTANT**: EXPLICIT USER CONSENT is REQUIRED to:
 - transition from PLANNING to IMPLEMENTATION
 - transition from CHECK to DISCUSSION

EOF
exit 0
