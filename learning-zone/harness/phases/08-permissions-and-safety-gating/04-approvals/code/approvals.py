"""Approval flow with remembered 'always' decisions. Run:  python3 approvals.py"""


class Approvals:
    def __init__(self, decide):
        self.decide = decide               # (action_class, detail) -> "once"|"always"|"deny"
        self.always = set()

    def request(self, action_class, detail):
        if action_class in self.always:
            return True                    # remembered
        choice = self.decide(action_class, detail)
        if choice == "always":
            self.always.add(action_class)
            return True
        return choice == "once"


if __name__ == "__main__":
    ap = Approvals(decide=lambda cls, d: "always" if cls == "git" else "deny")
    print("git commit ->", ap.request("git", "git commit"))
    print("git push   ->", ap.request("git", "git push"))     # remembered, no re-ask
    print("rm -rf     ->", ap.request("rm", "rm -rf build"))
