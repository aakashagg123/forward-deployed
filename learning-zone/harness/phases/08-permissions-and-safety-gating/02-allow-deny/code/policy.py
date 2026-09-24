"""Pattern allow/deny lists with deny-wins precedence. Run:  python3 policy.py"""
import fnmatch


class PolicyList:
    def __init__(self, allow=(), deny=()):
        self.allow, self.deny = list(allow), list(deny)

    def _match(self, patterns, signature):
        return any(fnmatch.fnmatch(signature, p) for p in patterns)

    def decide(self, signature):           # e.g. "bash:git push origin main"
        if self._match(self.deny, signature):
            return "deny"                  # deny always wins
        if self._match(self.allow, signature):
            return "allow"
        return "ask"                       # fall through


if __name__ == "__main__":
    pol = PolicyList(allow=["bash:git *", "read:*"],
                     deny=["bash:git push*", "write:/etc/*"])
    for sig in ["bash:git status", "bash:git push origin", "write:/etc/hosts", "write:/tmp/x"]:
        print(f"{sig:25} -> {pol.decide(sig)}")
