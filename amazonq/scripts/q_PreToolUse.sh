#!/bin/zsh

EXEMPT_PATHS=(
    ".todo/*"
    "/tmp/*"
    "tasks/*"
)

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

hook_data=$(cat)
tool_name=$(echo "$hook_data" | jq -r '.tool_name')

if [[ "$tool_name" == "fs_write" ]]; then

    path=$(echo "$hook_data" | jq -r '.parameters.path')
    # some paths may be exempt
    is_path_exempt "$path" && exit 0
    # otherwise we ensure we are not in DAIC
    has_consent

elif [[ "$tool_name" == "execute_bash" ]]; then
    has_consent
fi

exit 0

