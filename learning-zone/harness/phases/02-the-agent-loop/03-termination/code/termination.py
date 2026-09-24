"""Layered termination: natural finish, hard max_steps, and loop detection.

The StopPolicy is separate from the loop so termination is testable in isolation.

Run:  python3 termination.py
"""
from dataclasses import dataclass, field


@dataclass
class StopPolicy:
    max_steps: int = 10
    seen: list = field(default_factory=list)        # signatures of past calls

    def check(self, step, calls):
        if not calls:
            return "done"                            # natural finish
        if step >= self.max_steps:
            return "max_steps"                       # hard ceiling
        sig = tuple(sorted((c["name"], str(c["args"])) for c in calls))
        if self.seen and sig == self.seen[-1]:
            return "loop"                            # same calls as last step
        self.seen.append(sig)
        return None                                  # keep going


def run(query, model, run_calls):
    history, policy = [{"role": "user", "content": query}], StopPolicy()
    for step in range(policy.max_steps + 1):
        msg = model(history)
        history.append({"role": "assistant", "content": msg["text"]})
        verdict = policy.check(step, msg["tool_calls"])
        if verdict == "done":
            return msg["text"]
        if verdict == "max_steps":
            return "stopped: step budget exhausted"
        if verdict == "loop":
            history.append({"role": "user",
                            "content": "You repeated a call. Try a different approach or finish."})
            continue
        history.append({"role": "user", "content": run_calls(msg["tool_calls"])})
    return "stopped: step budget exhausted"


if __name__ == "__main__":
    # A model that loops forever, asking for the same tool every step.
    def stuck_model(history):
        return {"text": "calling again", "tool_calls": [{"name": "noop", "args": {}}]}

    print(run("go", stuck_model, run_calls=lambda calls: "ok"))
    # -> after a nudge and the step ceiling: "stopped: step budget exhausted"

    # A model that finishes after one tool call.
    def good_model(history):
        n = sum(1 for m in history if m["role"] == "assistant")
        if n == 0:
            return {"text": "working", "tool_calls": [{"name": "noop", "args": {}}]}
        return {"text": "all done", "tool_calls": []}

    print(run("go", good_model, run_calls=lambda calls: "ok"))   # -> "all done"
