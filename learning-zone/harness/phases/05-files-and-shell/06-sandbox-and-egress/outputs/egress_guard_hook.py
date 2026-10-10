#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool: block commands that reach hosts not on the allowlist.

Reads the hook JSON on stdin. Exit 2 blocks the call and sends stderr to Claude.
Exit 0 with no output means "no opinion": the normal permission flow continues.

Install: copy this file and ../code/egress_guard.py into the same folder
(for example .claude/hooks/), then register this file under hooks.PreToolUse
with matcher "Bash". This hook is one layer. It parses command text.
It cannot see inside scripts, so pair it with the sandbox network allowlist.
"""
import json
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [here, os.path.join(here, "..", "code")]
from egress_guard import check  # noqa: E402


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("egress hook: stdin was not JSON", file=sys.stderr)
        return 2                                       # fail closed
    if event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command", "")
    allowed, reason = check(command)
    if allowed:
        return 0
    print(f"BLOCKED by egress guard: {reason}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
