"""A read-only plan-mode gate: block mutations until the plan is approved.

Run:  python3 plan_mode.py
"""
MUTATING = {"write", "edit", "bash"}


class PlanMode:
    def __init__(self):
        self.active = True
        self.plan = None

    def propose(self, plan):
        self.plan = plan
        return "plan ready for approval:\n" + plan

    def approve(self):
        self.active = False
        return "approved — exiting plan mode"

    def gate(self, tool):
        if self.active and tool in MUTATING:
            return f"blocked: '{tool}' not allowed in plan mode (read-only until approved)"
        return "allowed"


if __name__ == "__main__":
    pm = PlanMode()
    print("read  ->", pm.gate("read"))
    print("write ->", pm.gate("write"))
    pm.propose("1) edit api.py 2) add test")
    pm.approve()
    print("write ->", pm.gate("write"))
