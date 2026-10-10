#!/usr/bin/env python3
"""PreToolUse hook: deny any tool call that touches a .env file. Fails closed on any error.

Checks file_path for Read, Edit and Write, and every word of a Bash command.
Template files such as .env.example stay allowed.
It answers with JSON on stdout and exit code 0. (The other way to block is
exit code 2 with the reason on stderr, as the egress hook does.)

Register under hooks.PreToolUse with matcher "Read|Edit|Write|Bash".
"""
import json
import os
import shlex
import sys

TEMPLATES = (".env.example", ".env.sample", ".env.template")


def is_secret_env(path):
    name = os.path.basename(path.rstrip("/"))
    return (name == ".env" or name.startswith(".env.") or name.endswith(".env")) \
        and name not in TEMPLATES


def paths_in(event):
    tool_input = event.get("tool_input") or {}
    found = [tool_input[k] for k in ("file_path", "path") if isinstance(tool_input.get(k), str)]
    if event.get("tool_name") == "Bash":
        try:
            found += shlex.split(tool_input.get("command", ""), posix=True)
        except ValueError:
            found += tool_input.get("command", "").split()
    return found


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("event is not an object")
        bad = [p for p in paths_in(event) if is_secret_env(p)]
    except Exception as exc:                           # any failure blocks the call
        print(f"env hook: cannot read the event ({exc})", file=sys.stderr)
        return 2                                       # fail closed
    if not bad:
        return 0                                       # no opinion
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"{bad[0]} holds secrets; the agent may not touch it",
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
