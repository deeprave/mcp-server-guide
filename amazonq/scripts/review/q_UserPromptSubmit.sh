#!/bin/bash
cat <<EOF
🚨 REVIEW ONLY - YOU MUST NOT MAKE ANY CHANGES TO THIS PROJECT

 - Review all changes for correctness, accuracy, functionality and security
 - Ensure no repeated patterns of re-implementations of existing code blocks or implementation of functionality
   already done by a well-known and established third party library or the standard library itself.
 - It is important to check the codebase for duplications even if not included in changes.
 - Ensure that no "dead code" remains which is not referenced or used anywhere in the code base,
   and otherwise does not exist for well-known and documented reasons.
 - Focus on the most important failures first.
 - Provide a detailed review including source files, line numbers and function names
   BE VERY SPECIFIC.
EOF
exit 0
