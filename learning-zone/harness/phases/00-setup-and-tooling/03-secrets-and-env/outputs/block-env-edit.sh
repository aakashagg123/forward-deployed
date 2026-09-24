#!/usr/bin/env bash
# PreToolUse hook: deny any Edit/Write whose path touches a .env file.
# Reads the tool-call JSON on stdin; exit 2 = deny (message on stderr).
input="$(cat)"
path="$(printf '%s' "$input" | grep -oE '"(file_path|path)"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*"([^"]*)"$/\1/')"
case "$path" in
  *.env|*.env.*|*/.env) echo "BLOCKED: edits to .env are not allowed" >&2; exit 2 ;;
  *) exit 0 ;;
esac
