"""A model of Claude Code hooks: external commands, JSON on stdin, exit-code protocol.

This is a MODEL of the idea, not Claude Code itself. Run:  python3 code/hooks.py
"""
import json
import os
import re
import subprocess
import sys


def matches(matcher, tool):
    """Letters, digits, _ - space , | mean an exact list. Anything else is a regex."""
    if matcher in ("", "*"):
        return True
    if re.fullmatch(r"[\w ,|-]+", matcher):
        return tool in re.split(r"\s*[|,]\s*", matcher)
    return re.search(matcher, tool) is not None


class HookRunner:
    def __init__(self):
        self.hooks = {"PreToolUse": [], "PostToolUse": []}     # (matcher, argv)

    def add(self, event, matcher, argv):
        self.hooks[event].append((matcher, argv))

    def _run(self, argv, payload):
        p = subprocess.run(argv, input=json.dumps(payload), capture_output=True,
                           text=True, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def pre(self, tool, tool_input):
        """Return ("deny", reason) or ("none", ""). A hook never needs to say allow."""
        event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
        for matcher, argv in self.hooks["PreToolUse"]:
            if not matches(matcher, tool):
                continue
            code, out, err = self._run(argv, event)
            if code == 2:                                       # blocking error
                return "deny", err.strip()
            if code == 0 and out.strip().startswith("{"):
                decision = json.loads(out).get("hookSpecificOutput", {})
                if decision.get("permissionDecision") == "deny":
                    return "deny", decision.get("permissionDecisionReason", "")
            # any other exit code is a non-blocking error: the call goes on
        return "none", ""

    def post(self, tool, tool_input, result):
        """The tool already ran. Exit 2 cannot undo it, but stderr goes back to the model."""
        event = {"hook_event_name": "PostToolUse", "tool_name": tool,
                 "tool_input": tool_input, "tool_response": result}
        for matcher, argv in self.hooks["PostToolUse"]:
            if matches(matcher, tool):
                code, _, err = self._run(argv, event)
                if code == 2:
                    result += f"\n[hook feedback] {err.strip()}"
        return result

    def call(self, tool, tool_input, execute, rules=None):
        verdict, reason = self.pre(tool, tool_input)
        if verdict == "deny":
            return f"blocked by hook: {reason}"
        if rules and rules(tool, tool_input) == "deny":         # a hook cannot override deny rules
            return "blocked by rule"
        return self.post(tool, tool_input, execute(tool, tool_input))


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    env_hook = [sys.executable, os.path.join(here, "..", "outputs", "block_env_hook.py")]
    lint = [sys.executable, "-c",
            "import json,sys; e=json.load(sys.stdin); "
            "sys.exit(0 if 'TODO' not in e['tool_response'] else (print('lint: TODO left in file', "
            "file=sys.stderr) or 2))"]
    crash = [sys.executable, "-c", "import sys; sys.exit(1)"]

    hr = HookRunner()
    hr.add("PreToolUse", "Read|Edit|Write|Bash", env_hook)
    hr.add("PostToolUse", "Write", lint)
    ran = []
    execute = lambda t, i: ran.append(t) or "wrote file"

    # Matcher rules.
    assert matches("Edit|Write", "Write") and not matches("Edit|Write", "Bash")
    assert matches("*", "Anything") and matches("mcp__.*__write.*", "mcp__fs__write_file")
    assert not matches("Edit", "MultiEdit")                      # exact, not substring

    # A Pre hook blocks before the tool runs. Nothing executes.
    out = hr.call("Edit", {"file_path": "/p/.env"}, execute)
    assert out.startswith("blocked by hook: /p/.env") and ran == []
    assert hr.call("Bash", {"command": "cat .env"}, execute).startswith("blocked by hook")
    # An unrelated call passes, and the Post hook adds feedback after the result.
    assert hr.call("Write", {"file_path": "app.py"}, execute) == "wrote file" and ran == ["Write"]
    out = hr.call("Write", {"file_path": "app.py"}, lambda t, i: "x = 1  # TODO")
    assert out.endswith("[hook feedback] lint: TODO left in file")

    # Exit 2 blocks. Any other failing exit code does NOT block. Write hooks to fail closed.
    hr.add("PreToolUse", "Bash", crash)
    assert hr.call("Bash", {"command": "ls"}, execute) == "wrote file"
    block2 = [sys.executable, "-c", "import sys; print('nope', file=sys.stderr); sys.exit(2)"]
    hr.add("PreToolUse", "Bash", block2)
    assert hr.call("Bash", {"command": "ls"}, execute) == "blocked by hook: nope"

    # A hook is not the last word: a deny rule still applies when no hook objects.
    hr2 = HookRunner()
    assert hr2.call("Bash", {"command": "rm -rf x"}, execute, rules=lambda t, i: "deny") == "blocked by rule"
    print("ok: hooks blocked, passed, crashed open, and deferred to deny rules")
