#!/bin/bash
set -e
set -u
set -o pipefail

hook_data=$(cat)

if [[ -f .hook_log ]]; then
  log_dir=$HOME/.kiro/logs
  mkdir -p $log_dir
  log_file="${log_dir}/hook.log"
  mkdir -p "$(dirname "$log_file")"
  json_data=$(jq -c '.' <<<"$hook_data" || true)
  function logger() {
    local data="$*"
    echo "$(date '+%Y-%m-%d %H:%M:%S')" "$data" >> "$log_file"
  }
  logger "guide: $json_data"
else
  function logger() {
    # shellcheck disable=SC2317
    local no_op
  }
fi

# ---------------- Paths allowlist (glob patterns)
EXEMPT_PATHS=(
  '.consent'
  '.issue'
  '.todo/**'
  '/tmp/**'
  'tasks/**'
  'specs/**'
  'openspec/**'
)

# ---------------- Command allowlist patterns (ERE for bash)
# Bash uses Extended Regular Expressions with [[ =~ ]]
EXEMPT_COMMAND_PATTERNS=(
  '^(cat|find|grep|tree|hostname|df|du|pwd|env|jq|ls|rg|acli|which)([[:space:]]|$)'
  '^rm[[:space:]]+(-f[[:space:]]+)?(\.consent|\.issue)$'
  '^git$'
  '^git[[:space:]]+(status|log|rev-parse|ls-files)([[:space:]].*)?$'
  '^git[[:space:]]+diff([[:space:]].*)?$'
  '^git[[:space:]]+show([[:space:]].*)?$'
)

# ---------------- Timeout command detection
TIMEOUT=60
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD=(timeout $TIMEOUT)
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_CMD=(gtimeout $TIMEOUT)
else
  TIMEOUT_CMD=()  # no timeout available
fi

# Multiline message: use a here-doc into a variable
read -r -d '' deny_message <<'EOF' || true
Attempted changes are not permitted in DISCUSSION/PLANNING phase
EOF

# ---------------- Path allowlist check
  # ---------------- Path allowlist check
  is_path_exempt() {
    local path=$1
    local pattern

    [[ "$path" == "$PWD"/* ]] && path="${path#$PWD/}"
    [[ "$path" == "$PWD" ]] && path=.
    for pattern in "${EXEMPT_PATHS[@]}"; do
      # Use bash pattern matching
      if [[ $path == $pattern ]]; then
        logger "path: $path == $pattern"
        exit 0
      fi
    done
    logger "path $path != $pattern"
  }

# ---------------- Command allowlist check
is_command_exempt() {
  local input="$1"
  local head rest re

  # Trim leading spaces
  input="${input#"${input%%[![:space:]]*}"}"

  # Handle cd commands chained with &&
  while [[ $input =~ ^cd[[:space:]]+[^'&']*'&&'[[:space:]]*(.*)$ ]]; do
    # Extract the remaining command after the last &&
    input="${BASH_REMATCH[1]}"
  done

  # Extract argv0 (command name) and strip any path
  read -r head rest <<< "$input"
  head="${head##*/}"  # Remove path if present

  # Rebuild command with bare command name
  if [[ -n $rest ]]; then
    input="$head $rest"
  else
    input="$head"
  fi

  # Check against exempt patterns
  for re in "${EXEMPT_COMMAND_PATTERNS[@]}"; do
    if [[ $input =~ $re ]]; then
      logger "command: $input =~ $re"
      exit 0
    fi
  done

  logger "command: $input !~ $re"
}

has_consent() {
  if [[ ! -f .consent ]]; then
    printf '%s\n' "$deny_message" >&2
    exit 2
  fi
}

ask_consent() {
  if [[ ! -f .consent ]]; then
    local message="$1"
    local response

    if command -v osascript >/dev/null 2>&1; then
      # macOS dialog
      if (( ${#TIMEOUT_CMD[@]} )); then
        response=$("${TIMEOUT_CMD[@]}" osascript -e "display dialog \"$message\" buttons {\"Deny\", \"Approve\"} default button \"Deny\"" 2>/dev/null || true)
      else
        response=$(osascript -e "display dialog \"$message\" buttons {\"Deny\", \"Approve\"} default button \"Deny\"" 2>/dev/null || true)
      fi
      if [[ $response == *Approve* ]]; then
        exit 0
      fi

    elif command -v zenity >/dev/null 2>&1; then
      # Linux dialog (zenity has its own --timeout)
      if zenity --question --text="$message" --timeout=$TIMEOUT 2>/dev/null; then
        exit 0
      fi
    fi

    printf '%s\n' "$deny_message" >&2
    exit 2
  fi
}

# ---------------- Main
tool_name="$(jq -r '.tool_name // empty' <<<"$hook_data")"

if [[ $tool_name == "fs_write" ]]; then
  path="$(jq -r '.tool_input.path // empty' <<<"$hook_data")"
  if is_path_exempt "$path"; then
    exit 0
  fi
  has_consent

elif [[ $tool_name == "execute_bash" ]]; then
  command="$(jq -r '.tool_input.command // "No command found"' <<<"$hook_data")"
  summary="$(jq -r '.tool_input.summary // empty' <<<"$hook_data")"

  message="You are in DISCUSSION/PLANNING phase
Do you approve the following shell command?

Command: $command"
  if [[ -n $summary && $summary != null ]]; then
    message="$message
Summary: $summary"
  fi

  if is_command_exempt "$command"; then
    exit 0
  fi
  ask_consent "$message"
fi

exit 0