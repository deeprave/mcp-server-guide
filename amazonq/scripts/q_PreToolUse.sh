#!/bin/zsh

EXEMPT_PATHS=(
    ".todo/*"
    "/tmp/*"
    "tasks/*"
)
TIMEOUT=60

function is_path_exempt() {
    local check_path="$1"
    # Convert absolute path to relative if it starts with current directory
    local relative_path="${check_path#$PWD/}"

    for pattern in "${EXEMPT_PATHS[@]}"; do
        if [[ "$relative_path" == $pattern ]]; then
            return 0
        fi
    done
    return 1
}

function has_consent() {
    if [ ! -f ".consent" ]; then
        echo "DAIC MODE IS ENABLED - CONSENT REQUIRED - Request approval before making changes." >&2
        exit 2
    fi
}

function ask_consent() {
    if [ ! -f ".consent" ]; then
        local message="$1"
        # Use osascript (macOS) or zenity (Linux) for GUI prompt
        if command -v osascript >/dev/null 2>&1; then
            response=$(timeout $TIMEOUT osascript -e "display dialog \"$message\" buttons {\"Deny\", \"Approve\"} default button \"Deny\"" 2>/dev/null)
            if [[ "$response" == *"Approve"* ]]; then
                exit 0
            fi
        elif command -v zenity >/dev/null 2>&1; then
            # Linux with zenity
            zenity --question --text="$message" --timeout=$TIMEOUT 2>/dev/null && exit 0
        fi
        echo "DAIC MODE ENABLED - CONSENT REQUIRED - Request approval before making changes." >&2
        exit 2
    fi
}

hook_data=$(cat)
tool_name=$(echo "$hook_data" | jq -r '.tool_name')

if [[ "$tool_name" == "fs_write" ]]; then

    path=$(echo "$hook_data" | jq -r '.tool_input.path')
    # some paths may be exempt
    is_path_exempt "$path" && exit 0
    # otherwise we ensure we are not in DAIC
    has_consent

elif [[ "$tool_name" == "execute_bash" ]]; then
    command=$(echo "$hook_data" | jq -r '.tool_input.command // "No command found"')
    summary=$(echo "$hook_data" | jq -r '.tool_input.summary // empty')

    message="DAIC MODE: Approve this bash command?
Command: $command"

    # Only add summary line if summary exists and is not empty
    if [[ -n "$summary" && "$summary" != "null" ]]; then
        message="$message
Summary: $summary"
    fi

    ask_consent "$message"
fi

exit 0

