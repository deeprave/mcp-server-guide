#!/bin/zsh
if [[ ! -f ".consent" ]]; then
  cat << 'EOF'
🚨 MANDATORY REMINDER: Before ANY implementation or architectural changes:
  1. Create detailed plan
  2. Request explicit user consent
  3. Wait for approval
  4. **NO EXCEPTIONS**
EOF
fi
exit 0
