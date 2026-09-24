"""Allow/ask/deny permission gate. Run:  python3 permission_modes.py"""

ALLOW, ASK, DENY = "allow", "ask", "deny"


class PermissionGate:
    def __init__(self, default=ASK, rules=None):
        self.default = default
        self.rules = rules or []           # list of (predicate, mode)

    def decide(self, tool, args):
        for predicate, mode in self.rules:
            if predicate(tool, args):
                return mode
        return self.default

    def run(self, tool, args, execute, confirm):
        mode = self.decide(tool, args)
        if mode == DENY:
            return "denied by policy"
        if mode == ASK and not confirm(tool, args):
            return "denied by user"
        return execute(tool, args)


if __name__ == "__main__":
    gate = PermissionGate(default=ASK, rules=[
        (lambda t, a: t in ("read", "grep", "glob"), ALLOW),
        (lambda t, a: t == "bash" and "rm -rf" in a.get("cmd", ""), DENY),
    ])
    print("read   ->", gate.decide("read", {}))
    print("rm -rf ->", gate.decide("bash", {"cmd": "rm -rf /"}))
    print("write  ->", gate.decide("write", {}))
