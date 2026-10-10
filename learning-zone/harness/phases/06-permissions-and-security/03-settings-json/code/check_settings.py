"""Lint a Claude Code settings.json, then run it through the lesson 01 gate.

Run:  python3 code/check_settings.py
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASES = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "..", "01-permission-gate", "code"))
from permission_gate import ALLOW, ASK, DENY, PermissionGate  # noqa: E402

HOOK_DIRS = [os.path.join(PHASES, "06-permissions-and-security", "02-hooks", "outputs"),
             os.path.join(PHASES, "05-files-and-shell", "06-sandbox-and-egress", "outputs")]
INERT = {"Write", "NotebookEdit", "Glob", "MultiEdit"}   # accepted, but never consulted


def lint(settings):
    """Return a list of problems. An empty list means the file looks right."""
    problems = []
    perms = settings.get("permissions", {})
    for kind in ("allow", "ask", "deny"):
        for rule in perms.get(kind, []):
            m = re.fullmatch(r"(\w+)(?:\((.*)\))?", rule)
            if not m:
                problems.append(f"{kind}: {rule!r} is not Tool or Tool(specifier)")
                continue
            tool, spec = m.groups()
            if tool in INERT and spec:
                problems.append(f"{rule}: path rules for {tool} are never consulted; use Edit(...) or Read(...)")
            if tool == "Bash" and spec:
                if re.match(r"command:", spec):
                    problems.append(f"{rule}: matching on the command field is ignored")
                if ":*" in spec[:-2]:
                    problems.append(f"{rule}: ':*' only works at the end of a pattern")
                if kind == "allow" and re.match(r"\w+ \* ", spec):
                    problems.append(f"{rule}: put the * after the subcommand")
    for event, groups in settings.get("hooks", {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                if hook.get("type") != "command" or "command" not in hook:
                    problems.append(f"{event}: hook needs type 'command' and a command")
                    continue
                script = hook["command"].split("/")[-1]
                if not any(os.path.isfile(os.path.join(d, script)) for d in HOOK_DIRS):
                    problems.append(f"{event}: hook script {script} does not exist")
    return problems


def smoke_hooks(settings):
    """Run every hook once with a harmless Bash event. Each must exit 0 and not deny."""
    event = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                        "tool_input": {"command": "ls"}})
    for groups in settings.get("hooks", {}).values():
        for group in groups:
            for hook in group["hooks"]:
                script = hook["command"].split("/")[-1]
                path = next(os.path.join(d, script) for d in HOOK_DIRS
                            if os.path.isfile(os.path.join(d, script)))
                p = subprocess.run([sys.executable, path], input=event, capture_output=True, text=True)
                assert p.returncode == 0 and "deny" not in p.stdout, (script, p)


if __name__ == "__main__":
    with open(os.path.join(HERE, "..", "outputs", "settings.json")) as f:
        settings = json.load(f)
    assert lint(settings) == [], lint(settings)
    smoke_hooks(settings)

    # The lint must be able to fail. Each broken copy is caught.
    broken = json.loads(json.dumps(settings))
    broken["permissions"]["allow"] += ["Write(src/**)", "Glob(*)", "Bash(git:* push)",
                                       "Bash(command:rm *)", "Bash(git * main)", "Bash(npm test"]
    broken["hooks"]["PostToolUse"] = [{"hooks": [{"type": "command", "command": ".claude/hooks/missing.sh"}]}]
    found = lint(broken)
    for needle in ("Write(src/**)", "Glob(*)", "git:* push", "command:rm", "git * main",
                   "npm test", "missing.sh"):
        assert any(needle in p for p in found), (needle, found)

    # Run the real rules through the gate model: deny, ask, allow, in that order.
    p = settings["permissions"]
    gate = PermissionGate(allow=p["allow"], ask=p["ask"], deny=p["deny"])
    assert gate.decide("Bash", "npm run test --watch") == ALLOW
    assert gate.decide("Bash", "git commit -m wip") == ASK
    assert gate.decide("Bash", "git push origin main") == DENY
    assert gate.decide("Bash", "git diff && git push") == DENY
    assert gate.decide("Read", "./.env") == DENY
    assert gate.decide("Edit", "src/app.py") == ASK                 # nothing matched: default mode
    print("ok: settings.json lints clean, hooks run, rules behave")
