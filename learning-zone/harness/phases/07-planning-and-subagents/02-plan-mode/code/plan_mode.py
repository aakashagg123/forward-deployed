"""A model of plan mode: read-only until a human approves a plan.

This is a teaching model of the idea, not Claude Code's code.
Run:  python3 code/plan_mode.py
"""
READ_ONLY_TOOLS = {"read", "glob", "grep"}
READ_ONLY_COMMANDS = {"ls", "cat", "git status", "git diff", "git log"}


class PlanMode:
    def __init__(self):
        self.state = "planning"          # planning -> awaiting_approval -> acting
        self.plan = None

    def gate(self, tool, command=None):
        """Return 'allow' or 'deny: <reason>' for one tool call."""
        if self.state == "acting":
            return "allow"
        if tool in READ_ONLY_TOOLS:
            return "allow"
        if tool == "bash" and command in READ_ONLY_COMMANDS:
            return "allow"                # exploring with a read-only command is fine
        return f"deny: '{tool}' is blocked until a plan is approved"

    def propose(self, plan):
        self.plan = plan
        self.state = "awaiting_approval"
        return "plan ready for approval:\n" + plan

    def decide(self, approved, feedback=""):
        if self.state != "awaiting_approval":
            raise ValueError("no plan to decide on")
        if approved:
            self.state = "acting"
            return "approved: exiting plan mode"
        self.state = "planning"           # stay read-only and revise
        self.plan = None
        return "rejected: revise the plan. " + feedback


if __name__ == "__main__":
    pm = PlanMode()
    assert pm.gate("read") == "allow"
    assert pm.gate("bash", "git status") == "allow"
    assert pm.gate("edit").startswith("deny")
    assert pm.gate("bash", "rm -rf build").startswith("deny")

    pm.propose("1) edit api.py  2) add a test")
    assert pm.gate("edit").startswith("deny")        # proposing is not approval

    pm.decide(False, "also cover the error path")
    assert pm.state == "planning" and pm.gate("edit").startswith("deny")

    pm.propose("1) edit api.py  2) add a test  3) test the error path")
    pm.decide(True)
    assert pm.gate("edit") == "allow"
    print("plan mode model: all checks passed")
