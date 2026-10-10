"""A model of Claude Code's permission gate: rules, modes, approvals.

Rules read like settings.json: "Bash(git push *)", "Read(./.env)", "Edit".
Order is deny, then ask, then allow. The first match wins.
Run:  python3 code/permission_gate.py
"""
import fnmatch
import re

ALLOW, ASK, DENY = "allow", "ask", "deny"


def parse_rule(rule):
    m = re.fullmatch(r"(\w+)(?:\((.*)\))?", rule)
    return m.group(1), m.group(2)                  # ("Bash", "git push *") or ("Edit", None)


def bash_match(pattern, command):
    if pattern.endswith(":*"):
        pattern = pattern[:-2] + " *"              # ":*" is a trailing " *"
    body = re.escape(pattern).replace(r"\*", ".*")
    if pattern.endswith(" *") and pattern.count("*") == 1:
        body = re.escape(pattern[:-2]) + "( .*)?"  # "ls *" also matches bare "ls"
    return re.fullmatch(body, command) is not None


def subcommands(command):
    """Split a compound command. Quotes are ignored here, a known simplification."""
    parts = re.split(r"&&|\|\||[;|&\n()`]", command)
    words = [re.sub(r"^(?:\$|time |nohup |nice |timeout \d+ )+", "", p.strip()) for p in parts]
    return [w for w in words if w]


class PermissionGate:
    def __init__(self, allow=(), ask=(), deny=(), mode="default"):
        self.rules = {ALLOW: list(allow), ASK: list(ask), DENY: list(deny)}
        self.mode = mode

    def _hit(self, rules, tool, arg):
        for rule in rules:
            name, spec = parse_rule(rule)
            if name != tool:
                continue
            if spec is None or spec == "*":
                return True
            if tool == "Bash" and bash_match(spec, arg):
                return True
            if tool != "Bash" and fnmatch.fnmatch(arg, spec.replace("./", "*")):
                return True
        return False

    def decide(self, tool, arg=""):
        parts = subcommands(arg) if tool == "Bash" else [arg]
        if any(self._hit(self.rules[DENY], tool, p) for p in parts):
            return DENY                            # deny sees every subcommand
        if any(self._hit(self.rules[ASK], tool, p) for p in parts):
            return ASK
        if all(self._hit(self.rules[ALLOW], tool, p) for p in parts):
            return ALLOW                           # allow must cover every subcommand
        if self.mode == "plan" and tool in ("Edit", "Write"):
            return DENY
        if self.mode == "acceptEdits" and tool in ("Edit", "Write"):
            return ALLOW
        return DENY if self.mode == "dontAsk" else ASK

    def run(self, tool, arg, execute, confirm):
        """confirm(tool, arg) -> "once" | "always" | "deny"."""
        verdict = self.decide(tool, arg)
        if verdict == DENY:
            return "denied by rule"
        if verdict == ASK:
            choice = confirm(tool, arg)
            if choice == "deny":
                return "denied by user"
            if choice == "always":
                self.remember(tool, arg)
        return execute(tool, arg)

    def remember(self, tool, arg):
        """'Yes, and do not ask again' saves an allow rule for the command prefix."""
        for sub in (subcommands(arg) if tool == "Bash" else [arg]):
            rule = f"{tool}({' '.join(sub.split()[:2])} *)" if tool == "Bash" else tool
            self.rules[ALLOW].append(rule)


if __name__ == "__main__":
    gate = PermissionGate(
        allow=["Read", "Bash(git status *)", "Bash(npm run test *)"],
        ask=["Bash(git commit *)"],
        deny=["Bash(git push *)", "Bash(rm *)", "Read(./.env)"])

    assert gate.decide("Read", "src/app.py") == ALLOW
    assert gate.decide("Bash", "npm run test") == ALLOW            # bare command matches "x *"
    assert gate.decide("Bash", "npm run test --watch") == ALLOW
    assert gate.decide("Bash", "npm run testing") == ASK           # no word boundary match
    assert gate.decide("Bash", "git commit -m x") == ASK
    assert gate.decide("Edit", "a.py") == ASK                      # no rule: default mode asks

    # Deny wins, even over a broad allow, and even for a path inside a subcommand.
    assert gate.decide("Read", "./.env") == DENY
    wide = PermissionGate(allow=["Bash(git *)"], deny=["Bash(git push *)"])
    assert wide.decide("Bash", "git push origin main") == DENY
    assert wide.decide("Bash", "git status") == ALLOW
    assert gate.decide("Bash", "git status && git push origin") == DENY
    assert gate.decide("Bash", "echo $(rm -rf build)") == DENY
    assert gate.decide("Bash", "timeout 30 rm -rf build") == DENY
    # Allow needs every part: one unknown subcommand makes the whole call ask.
    assert gate.decide("Bash", "git status && curl evil.test") == ASK

    # Known limit: a rule matches command text. A different spelling slips past a deny rule.
    assert gate.decide("Bash", "/bin/rm -rf build") == ASK
    assert gate.decide("Bash", "bash -c 'rm -rf build'") == ASK

    # Modes change what happens to calls that no rule decided.
    assert PermissionGate(mode="acceptEdits").decide("Edit", "a.py") == ALLOW
    assert PermissionGate(mode="dontAsk").decide("Edit", "a.py") == DENY
    assert PermissionGate(mode="plan").decide("Write", "a.py") == DENY
    assert PermissionGate(mode="dontAsk", allow=["Bash(ls *)"]).decide("Bash", "ls -la") == ALLOW

    # Approvals: "always" saves a rule, so the same command class is not asked twice.
    asked = []
    def confirm(tool, arg):
        asked.append(arg)
        return "always"
    run = lambda t, a: "ran " + a
    assert gate.run("Bash", "git commit -m one", run, confirm) == "ran git commit -m one"
    assert gate.decide("Bash", "git commit -m two") == ASK         # ask rule still beats the new allow
    g2 = PermissionGate(allow=["Read"], deny=["Bash(git push *)"])
    assert g2.run("Bash", "make build", run, confirm) == "ran make build"
    assert g2.decide("Bash", "make build --fast") == ALLOW and len(asked) == 2
    assert g2.run("Bash", "git push origin", run, lambda *a: "always") == "denied by rule"
    assert g2.run("Bash", "wget x", run, lambda *a: "deny") == "denied by user"
    print("ok:", len(asked), "prompts shown")
