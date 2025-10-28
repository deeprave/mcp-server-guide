#!/bin/zsh
# Safer option setup in zsh (avoid bash-y combined flags)
set -e
set -u
set -o pipefail

# Enable extended globbing for recursive ** patterns
setopt extended_glob 2>/dev/null || true

# ---------------- Paths allowlist (glob patterns)
EXEMPT_PATHS=(
  ".consent"
  ".issue"
  ".todo/**"
  "/tmp/**"
  "tasks/**"
  "specs/**"
)

# ---------------- Commands allowlist (regex patterns)
# Prefer PCRE; fall back to ERE if PCRE isn't enabled.
# PCRE allows \b, \s, (?:...), etc.
setopt RE_MATCH_PCRE 2>/dev/null || true

EXEMPT_COMMAND_PATTERNS_PCRE=(
  '^(?:cat|find|grep|tree|hostname|df|du|pwd|env|jq|ls|rg|acli|which)\b'
  '^git(?:\s+(?:status|log|rev-parse|ls-files))?\s*$'
  '^git(?:\s+diff(?:\s+--name-only)?\s*)$'
  '^git(?:\s+show(?:\s+--name-only)?\s*)$'
)

# POSIX ERE fallback (no \b, so use ([[:space:]]|$))
EXEMPT_COMMAND_PATTERNS_ERE=(
  '^(cat|find|grep|tree|hostname|df|du|pwd|env|jq|ls|rg|acli|which)([[:space:]]|$)'
  '^git([[:space:]]+(status|log|rev-parse|ls-files)([[:space:]]|$))?$'
  '^git([[:space:]]+diff([[:space:]]+--name-only)?([[:space:]]|$))$'
  '^git([[:space:]]+show([[:space:]]+--name-only)?([[:space:]]|$))$'
)

# ---------------- Redirection guard (PCRE or ERE versions)
writes_redirect_pcre() {
  [[ $1 =~ '(^|\s)(>>|&>|[0-9]?>|<<<)(\s|$)' ]]
}
writes_redirect_ere() {
  [[ $1 =~ '(^|[[:space:]])(>>|&>|[0-9]?>|<<<)([[:space:]]|$)' ]]
}

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
You are in DISCUSSION/PLANNING phase
- Changes are currently not permitted
EOF

# ---------------- Path allowlist check
is_path_exempt() {
  local check_path="$1"

  # Absolute form
  if [[ $check_path != /* ]]; then
    check_path="$PWD/${check_path#./}"
  fi
  local abs="$check_path"

  # Project-relative form
  local rel="${abs#$PWD/}"
  rel="${rel#./}"

  local pattern candidate
  for pattern in "${EXEMPT_PATHS[@]}"; do
    if [[ $pattern == /* ]]; then
      candidate="$abs"
    else
      candidate="$rel"
    fi
    # Unquoted RHS to enable globbing
    if [[ $candidate == $pattern ]]; then
      return 0
    fi
  done
  return 1
}

# ---------------- Command allowlist check
is_command_exempt() {
  emulate -L zsh
  # Keep zsh’s regex capture variables local to this function
  local MATCH MBEGIN MEND
  local -a match mbegin mend

  local input="$1" head rest re

# Trim leading spaces
  input=${input##[[:space:]]#}

  # Strip one or more leading "cd <dir> &&" prefixes, handling quoted and unquoted directory names,
  # and allowing for multiple chained cd commands.
  # This regex matches:
  #   - cd 'dir with spaces' &&
  #   - cd "dir with spaces" &&
  #   - cd dir_with_no_spaces &&
  #   - with arbitrary whitespace
  # It will not break on && inside quotes.
  while [[ $input =~ ^cd[[:space:]]+((\"([^\"]*)\")|(\'([^\']*)\')|([^\'\"\&\;]+))[[:space:]]*&&[[:space:]]*(.*)$ ]]; do
    # Extract the remaining command after the last &&
    input="${match[6]}"
  done

  # Extract argv0 and strip any path
  head=${input%%[[:space:]]*}
  head=${head##*/}

  # Remainder
  rest=${input#"$head"}
  rest=${rest##[[:space:]]#}  # drop any leading spaces in rest

  # Rebuild "head + rest" so ^ anchors apply to the bare name
  if [[ -n $rest ]]; then
    input="$head $rest"
  else
    input="$head"
  fi

  if [[ -o RE_MATCH_PCRE ]]; then
    for re in "${EXEMPT_COMMAND_PATTERNS_PCRE[@]}"; do
      if [[ $input =~ $re ]]; then
        writes_redirect_pcre "$1" && return 1
        return 0
      fi
    done
  else
    for re in "${EXEMPT_COMMAND_PATTERNS_ERE[@]}"; do
      if [[ $input =~ $re ]]; then
        writes_redirect_ere "$1" && return 1
        return 0
      fi
    done
  fi

  return 1
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
      if (( ${#TIMEOUT_CMD[@]} )); then
        response=$("${TIMEOUT_CMD[@]}" osascript -e "display dialog \"$message\" buttons {\"Deny\", \"Approve\"} default button \"Deny\"" 2>/dev/null || true)
      else
        response=$(osascript -e "display dialog \"$message\" buttons {\"Deny\", \"Approve\"} default button \"Deny\"" 2>/dev/null || true)
      fi
      [[ $response == *Approve* ]] && exit 0

    elif command -v zenity >/dev/null 2>&1; then
      # zenity has its own --timeout
      zenity --question --text="$message" --timeout=$TIMEOUT 2>/dev/null && exit 0
    fi

    printf '%s\n' "$deny_message" >&2
    exit 2
  fi
}

# ---------------- Main
hook_data="$(cat)"
# Debug echo (kept compact); remove if noisy
jq -c '.' <<<"$hook_data" || true

tool_name="$(jq -r '.tool_name // empty' <<<"$hook_data")"

if [[ $tool_name == "fs_write" ]]; then

  path="$(jq -r '.tool_input.path // empty' <<<"$hook_data")"
  is_path_exempt "$path" && exit 0
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

  is_command_exempt "$command" && exit 0
  ask_consent "$message"
fi

exit 0
