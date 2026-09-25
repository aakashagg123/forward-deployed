# Stop reasons & max tokens

> **Motto** — Why the model stopped tells the harness what to do next.

*Part of Phase 01 — LLM I/O Foundations.*

## The Problem

Every response carries a `stop_reason`. Treat them all the same and you get problems: a
half-finished answer sent to the user (truncated at `max_tokens`), or tools the model
asked for that never run. The harness's next action depends on the stop reason, so make
that mapping explicit.

## The Concept

The common stop reasons and the correct harness response:

| stop_reason | meaning | harness action |
| --- | --- | --- |
| `end_turn` | model finished naturally | return the text |
| `tool_use` | model requested tools | run them, loop again |
| `max_tokens` | hit the output cap | continue generation or raise the cap |
| `stop_sequence` | hit a configured stop string | return up to the stop |

<style>
.dgm-stpr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-stpr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-stpr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-stpr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-stpr-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-stpr-branches{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.dgm-stpr-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-stpr-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-stpr-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-stpr-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-stpr-b.accent h6{color:#0d5c0d}
.dgm-stpr-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-stpr-b.blue h6{color:#0550ae}
.dgm-stpr-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-stpr-b.green h6{color:#1a614f}
.dgm-stpr-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-stpr-b.red h6{color:#82061e}
.dgm-stpr-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-stpr-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-stpr{padding:20px 16px 18px}.dgm-stpr-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-stpr">
  <span class="dgm-stpr-chip">The stop_reason decides what happens next</span>
  <h4>Four stop reasons, four different next actions</h4>
  <p class="dgm-stpr-sub">Only tool_use loops back into the agent — the other three all end the turn.</p>
  <div class="dgm-stpr-q">response.stop_reason</div>
  <div class="dgm-stpr-branches">
    <div class="dgm-stpr-b green">
      <h6>end_turn</h6>
      <p>Return</p>
    </div>
    <div class="dgm-stpr-b accent">
      <h6>tool_use</h6>
      <p>Run tools → loop</p>
    </div>
    <div class="dgm-stpr-b blue">
      <h6>max_tokens</h6>
      <p>Continue / raise cap</p>
    </div>
    <div class="dgm-stpr-b neutral">
      <h6>stop_sequence</h6>
      <p>Return to stop</p>
    </div>
  </div>
</div>


## Build It

`code/stop_reasons.py` — a dispatch that turns a stop reason into an action:

```python
def next_action(stop_reason, has_tool_calls):
    if stop_reason == "tool_use" and has_tool_calls:
        return "run_tools"
    if stop_reason == "end_turn":
        return "return"
    if stop_reason == "max_tokens":
        return "continue"          # response was truncated — generate more
    if stop_reason == "stop_sequence":
        return "return"
    return "return"                # unknown → safest is to return what we have

def continue_generation(messages, partial):
    """For max_tokens: append the partial assistant text and ask it to keep going."""
    return messages + [
        {"role": "assistant", "content": partial},
        {"role": "user", "content": "continue"},
    ]
```

```python
print(next_action("max_tokens", False))   # continue
print(next_action("tool_use", True))      # run_tools
print(next_action("end_turn", False))     # return
```

Handling `max_tokens` instead of silently truncating is the difference between a complete
answer and a mysterious cut-off.

## Use It

`msg.stop_reason` drives your loop (you used it in Phase 2 lesson 05). For long outputs,
either raise `max_tokens` or implement the continue pattern. For structured outputs,
configure a `stop_sequences` list so generation halts cleanly at a delimiter.

## Ship It

[`code/stop_reasons.py`](../../05-stop-reasons/code/stop_reasons.py) — a stop-reason → action
dispatcher with a continue-generation helper.

## Check Yourself

**Q1.** `stop_reason == "max_tokens"` means…

- A) the model finished
- B) the output was cut off at the cap — it may be incomplete
- C) a tool is needed
- D) an error

<details><summary>Answer</summary>B — truncation; continue or raise the cap.</details>

**Q2.** On `tool_use`, the harness should…

- A) return the text to the user
- B) execute the requested tools and loop again
- C) stop
- D) raise the token cap

<details><summary>Answer</summary>B — act, then continue the loop.</details>

**Challenge.** Add a guard so the continue pattern can't loop forever on `max_tokens`
(cap the number of continuations), tying back to Phase 2 termination.

## Related

- Builds on: [Streaming](../../04-streaming/docs/en.md)
- Used in: Phase 2 — [The Agent Loop](../../../02-the-agent-loop/01-agent-loop/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
