#!/usr/bin/env bash
# PostToolUse hook (Edit|Write|MultiEdit): auto-run `ruff check --fix` on the
# edited file when it's a Python source file. Best-effort; never blocks.
set -uo pipefail

proj="${CLAUDE_PROJECT_DIR:-.}"
f="$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')"
[ -n "$f" ] || exit 0

case "$f" in
  *.py) ;;
  *) exit 0 ;;
esac

ruff_bin="$proj/.venv/bin/ruff"
[ -x "$ruff_bin" ] || ruff_bin="$(command -v ruff || true)"
[ -n "$ruff_bin" ] || exit 0

"$ruff_bin" check --fix "$f" >/dev/null 2>&1 || true
exit 0
