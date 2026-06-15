#!/usr/bin/env bash
# PreToolUse hook (Edit|Write|MultiEdit): block writes that introduce
# secret-shaped content. Secret hygiene is the repo's top priority — keep
# credentials in Secret Manager, never in git.
set -uo pipefail

payload="$(cat)"
file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty')"

# Concatenate everything being written: Write.content, Edit.new_string,
# and every MultiEdit edit's new_string.
content="$(printf '%s' "$payload" | jq -r '
  [ .tool_input.content,
    .tool_input.new_string,
    ( .tool_input.edits[]?.new_string )
  ] | map(select(. != null)) | join("\n")
')"
[ -n "$content" ] || exit 0

deny() {
  jq -cn --arg r "$1" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
}

# 1. PEM private key blocks
if printf '%s' "$content" | grep -qE -- '-----BEGIN [A-Z ]*PRIVATE KEY-----'; then
  deny "Blocked: content contains a PEM private key. Store keys in Secret Manager, never in the repo."
fi

# 2. GCP service-account key JSON (no SA key files on disk — use ADC / attached SA)
if printf '%s' "$content" | grep -qE '"type"[[:space:]]*:[[:space:]]*"service_account"'; then
  deny "Blocked: looks like a GCP service-account key JSON. No SA keys on disk — use ADC locally and the attached SA on Cloud Run."
fi

# 3. High-confidence credential token shapes (AWS / GitHub / Google / Slack)
if printf '%s' "$content" | grep -qE '(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36}|AIza[0-9A-Za-z_-]{35}|xox[baprs]-[0-9A-Za-z-]{10,})'; then
  deny "Blocked: content contains a credential token (AWS/GitHub/Google/Slack). Move it to Secret Manager."
fi

# 4. .env must hold only non-secret config (TOOLS_* metadata). Flag a
#    high-entropy, secret-shaped value (mixed case + digit, length >= 16).
case "$file" in
  *.env)
    vals="$(printf '%s' "$content" | grep -vE '^[[:space:]]*#' | grep -oE '=[^[:space:]#]+' | sed 's/^=//')"
    if printf '%s' "$vals" | grep -E '.{16,}' | grep -E '[a-z]' | grep -E '[A-Z]' | grep -qE '[0-9]'; then
      deny ".env should hold non-secret config only. A secret-shaped value was detected — keep the value in Secret Manager and reference only the secret NAME here."
    fi
    ;;
esac

exit 0
