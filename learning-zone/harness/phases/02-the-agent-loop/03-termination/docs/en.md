# Termination: stop conditions & max steps

> **Motto** — An agent without a stop condition is a fork bomb with opinions.

*Part of Phase 02 — The Agent Loop. Builds on
[The agent loop from scratch](../../01-agent-loop/docs/en.md).*

## The Problem

The loop calls the model, runs tools, and calls again. What makes it *stop*? "When the
model stops asking for tools" is one answer, but a confused model can ask forever, repeat
the same call, or never emit a final answer. Without explicit ceilings, a single request
can run 40 steps and spend real money. Termination is not an afterthought. It's the
difference between an agent and a runaway bill.

## The Concept

A loop needs **layered** stop conditions, checked every iteration:

<style>
.dgm-term{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-term-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-term h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-term-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-term-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-term-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-term-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-term-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-term-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-term-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-term-b.accent h6{color:#0d5c0d}
.dgm-term-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-term-b.blue h6{color:#0550ae}
.dgm-term-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-term-b.green h6{color:#1a614f}
.dgm-term-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-term-b.red h6{color:#82061e}
.dgm-term-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-term-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-term{padding:20px 16px 18px}.dgm-term-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-term">
  <span class="dgm-term-chip">Three gates decide when a step ends</span>
  <h4>Natural finish, budget, or a repeated call — each ends the loop differently</h4>
  <p class="dgm-term-sub">A repeated call gets nudged before it burns the whole step budget.</p>
  <div class="dgm-term-q">Model asked for tools?</div>
  <div class="dgm-term-branches">
    <div class="dgm-term-b green">
      <h6>No</h6>
      <p>✅ Natural finish</p>
    </div>
    <div class="dgm-term-b accent">
      <h6>Yes — step budget left?</h6>
      <p>No → ⛔ max_steps · Yes, repeated call → nudge / break loop · Yes, new call → run tools, continue</p>
    </div>
  </div>
</div>


- **Natural:** the model returns no tool calls → done.
- **Hard ceiling:** `max_steps` — non-negotiable, always present.
- **Behavioral:** loop detection (same call twice), token/cost budget (Phase 14).
- **Explicit:** a `done` tool the model calls to signal completion.

## Build It

`code/termination.py` — a policy object the loop consults each step:

```python
from dataclasses import dataclass, field

@dataclass
class StopPolicy:
    max_steps: int = 10
    seen: list = field(default_factory=list)      # signatures of past calls

    def check(self, step, calls):
        if not calls:
            return "done"                          # natural finish
        if step >= self.max_steps:
            return "max_steps"                     # hard ceiling
        sig = tuple(sorted((c["name"], str(c["args"])) for c in calls))
        if self.seen and sig == self.seen[-1]:
            return "loop"                          # same calls as last step
        self.seen.append(sig)
        return None                                # keep going

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
            history.append({"role": "user", "content": "You repeated a call. Try a different approach or finish."})
            continue
        history.append({"role": "user", "content": run_calls(msg["tool_calls"])})
    return "stopped: step budget exhausted"
```

The policy is separate from the loop. That keeps termination rules testable in isolation
and reusable across agents.

## Use It

The SDK gives you `stop_reason` (`"end_turn"`, `"tool_use"`, `"max_tokens"`). That
covers *natural* and *token* termination. The **step**, **loop**, and **cost** ceilings
are yours to add — no SDK enforces them for you. That's the whole point of owning the
loop: the provider stops a single call, but only your harness stops a *runaway agent*.

## Ship It

[`code/termination.py`](../../03-termination/code/termination.py) — a `StopPolicy` you
compose into any loop.

## Check Yourself

**Q1.** Which stop condition must *always* be present, even if every other check is off?

- A) loop detection
- B) a hard `max_steps` ceiling
- C) a `done` tool
- D) token budget

<details><summary>Answer</summary>B — it's the backstop that guarantees the loop
terminates no matter how the model behaves.</details>

**Q2.** On detecting a repeated call, the better default is to…

- A) crash
- B) nudge the model to change approach and continue within budget
- C) silently re-run it
- D) return the previous result

<details><summary>Answer</summary>B — give the model a chance to recover; the step
ceiling still bounds the total.</details>

**Challenge.** Add a `max_tool_calls` ceiling (total across all steps), so a model that
asks for 5 tools per step can't blow the budget before hitting `max_steps`.

## Related

- Builds on: [The agent loop from scratch](../../01-agent-loop/docs/en.md)
- Next: [Turn history & conversation state](../../04-turn-history/docs/en.md)
- Concept: [Agent guardrails](../../../../ROADMAP.md)
