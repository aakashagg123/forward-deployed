# Use it: the agent loop on the real SDK

> **Motto** — Same loop, same invariants — the only new thing is the wire format.

*Part of Phase 02 — The Agent Loop. Builds on lessons 01–04.*

## The Problem

You've built the loop, the act step, termination, and history from scratch. Now wire
them to a real model so the agent actually does something. The risk at this step is
treating the SDK as magic and forgetting the invariants you just learned. It isn't
magic. It's the same loop with `tool_use` / `tool_result` content blocks instead of
plain dicts.

## The Concept

<style>
.dgm-stul{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-stul-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-stul h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-stul-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-stul-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-stul-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-stul-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-stul-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-stul-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-stul-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-stul-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-stul-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-stul{padding:20px 16px 18px}.dgm-stul-row{flex-direction:column}}
.dgm-stul-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-stul-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-stul-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-stul-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-stul-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-stul-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-stul-b.accent h6{color:#0d5c0d}
.dgm-stul-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-stul-b.blue h6{color:#0550ae}
.dgm-stul-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-stul-b.green h6{color:#1a614f}
.dgm-stul-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-stul-b.red h6{color:#82061e}
.dgm-stul-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-stul-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-stul{padding:20px 16px 18px}.dgm-stul-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-stul">
  <span class="dgm-stul-chip">The SDK's tool loop in five calls</span>
  <h4>stop_reason decides whether the SDK loops or returns</h4>
  <p class="dgm-stul-sub">tool_use always sends results back into the same messages.create call.</p>
  <div class="dgm-stul-row">
    <div class="dgm-stul-n neutral">User</div>
    <span class="dgm-stul-arr">→</span>
    <div class="dgm-stul-n accent">messages.create(tools=…)</div>
  </div>
  <div class="dgm-stul-q">stop_reason</div>
  <div class="dgm-stul-branches">
    <div class="dgm-stul-b blue">
      <h6>tool_use</h6>
      <p>Run tools → tool_result blocks → call again</p>
    </div>
    <div class="dgm-stul-b green">
      <h6>end_turn</h6>
      <p>Final text</p>
    </div>
  </div>
</div>


The mapping from your scratch version:

| Scratch | SDK |
| --- | --- |
| `model(history)` | `client.messages.create(model=…, tools=…, messages=…)` |
| `msg["tool_calls"]` | `[b for b in msg.content if b.type == "tool_use"]` |
| your `tool_result` dict | `{"type": "tool_result", "tool_use_id": id, "content": …}` |
| `StopPolicy` natural finish | `msg.stop_reason == "end_turn"` |

## Build It (wire it up)

`code/sdk_loop.py` — defaults to the latest model, **Claude Opus 5**
(`claude-opus-5`). Requires `pip install anthropic` and `ANTHROPIC_API_KEY`.

```python
import anthropic
client = anthropic.Anthropic()
MAX_STEPS = 10

TOOLS = {"add": lambda a, b: a + b}
SCHEMA = [{
    "name": "add", "description": "Add two numbers.",
    "input_schema": {"type": "object",
        "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        "required": ["a", "b"]},
}]

def run(query):
    messages = [{"role": "user", "content": query}]
    for _ in range(MAX_STEPS):
        msg = client.messages.create(
            model="claude-opus-5", max_tokens=1024, tools=SCHEMA, messages=messages)
        messages.append({"role": "assistant", "content": msg.content})
        calls = [b for b in msg.content if b.type == "tool_use"]
        if msg.stop_reason != "tool_use" or not calls:           # termination
            return "".join(b.text for b in msg.content if b.type == "text")
        results = []
        for call in calls:                                        # act step
            try:
                out = str(TOOLS[call.name](**call.input))
            except Exception as e:
                out = f"error: {e}"                               # errors are data
            results.append({"type": "tool_result", "tool_use_id": call.id, "content": out})
        messages.append({"role": "user", "content": results})     # pairing invariant
    return "stopped: hit MAX_STEPS"

if __name__ == "__main__":
    print(run("What is 12 + 30? Use the add tool."))
```

Every concept from lessons 01–04 is visible: termination (`stop_reason`), the act step
(parse `tool_use`, dispatch, errors-as-data), and the pairing invariant (results go back
in a `user` message keyed by `tool_use_id`).

## Use It (TypeScript)

The Node SDK is identical in shape — `@anthropic-ai/sdk`, `client.messages.create`,
`content.filter(b => b.type === 'tool_use')`, results returned as `tool_result` blocks.
Harnesses like Claude Code live in this ecosystem, so the loop you wrote ports directly.

## Ship It

[`code/sdk_loop.py`](../../05-sdk-tool-use-loop/code/sdk_loop.py) — a real, model-backed
agent loop you can point at any tool set.

## Check Yourself

**Q1.** Where do tool results go in the SDK conversation?

- A) in the next `assistant` message
- B) in a `user` message as `tool_result` blocks keyed by `tool_use_id`
- C) in the system prompt
- D) they're discarded

<details><summary>Answer</summary>B — results are sent back as a user turn, each paired
to the originating `tool_use_id`.</details>

**Q2.** `stop_reason == "end_turn"` means…

- A) run more tools
- B) the model is done — return its text
- C) an error occurred
- D) the token limit was hit

<details><summary>Answer</summary>B — natural finish. (`"max_tokens"` is the truncated
case; `"tool_use"` means act and continue.)</details>

**Challenge.** Replace the inline message list with the `History` class from lesson 04
and the `StopPolicy` from lesson 03, so this loop reuses your scratch modules instead of
re-implementing them.

## Related

- Builds on: lessons [01](../../01-agent-loop/docs/en.md)–[04](../../04-turn-history/docs/en.md)
- Next: [Error recovery inside the loop](../../06-error-recovery/docs/en.md)
