#!/bin/zsh
if [[ ! -f ".consent" ]]; then
  cat << 'EOF'
🚨 CONSENT TO CHANGE NOT GRANTED
You are in DISCUSSION or PLANNING mode and may not make any changes
REMINDER: Before ANY implementing changes you must have explicit user consent. **NO EXCEPTIONS**
EOF
else
  cat << 'EOF'
✅ CONSENT TO MAKE CHANGES GRANTED
You are in IMPLEMENTATION or CHECK mode.
Once you have completed implementation and checks you MUST remove the .consent and return to DISCUSSION mode.
EOF
fi
exit 0
