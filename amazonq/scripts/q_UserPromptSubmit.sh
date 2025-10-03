#!/bin/zsh
if [[ ! -f ".consent" ]]; then
  cat << 'EOF'
🚨 YOU ARE IN DAIC MODE
REMINDER: Before ANY implementation or architectural changes:
  1. Create detailed plan
  2. Request explicit user consent
  3. Wait for approval
  4. **NO EXCEPTIONS**
EOF
else
  cat << 'EOF'
✅ IMPLEMENTATION MODE
You may proceed with implementation and architectural changes.
If you have completed the implementation you MUST remove the .consent file to return to DAIC mode.
EOF
fi
exit 0
