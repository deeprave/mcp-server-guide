#!/bin/zsh
cat <<EOF
🚨 YOU MUST NOT MAKE ANY CHANGES TO THIS PROJECT

 - Review all changes for correctness, accuracy, functionality and security
 - Ensure no repeated patterns of re-implementations of existing code blocks.
   It is important to check the codebase for duplicated functionality even if not included in changes.
 - Ensure that no "dead code" remains which is not referenced or used anywhere in the code base,
   and otherwise does not exist for known reasons.
 - Focus on the most important failures first
 - Provide a detailed review including source files, line numbers and function names
   BE VERY SPECIFIC.

EOF
exit 0
