# Use it: SDK tool definitions & parallel tool use

> **Motto** — One model turn can request several tools at once — run them, return all results.

*Part of Phase 03 — Tool Engineering. Builds on the whole phase.*

## The Problem

You've built schemas, validation, results, idempotency, and budgets by hand. Now wire
them to the real SDK, and handle the case the toy loop glossed over: the model can emit
**multiple `tool_use` blocks in one turn**. If you only run the first, the model waits
forever for the rest. If you return results in the wrong shape, the API rejects them.

## The Concept

<style>
.dgm-spt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-spt-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-spt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-spt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-spt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-spt-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-spt-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-spt-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-spt-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-spt-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-spt-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-spt-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-spt{padding:20px 16px 18px}.dgm-spt-row{flex-direction:column}}
</style>
<div class="dgm-spt">
  <span class="dgm-spt-chip">Parallel tool calls resolve as one user turn</span>
  <h4>Several tool_use blocks in, one tool_result batch out</h4>
  <p class="dgm-spt-sub">Each call is validated, budgeted and dispatched independently — but they return together.</p>
  <div class="dgm-spt-row">
    <div class="dgm-spt-n neutral">Assistant turn</div>
    <span class="dgm-spt-arr">→</span>
    <div class="dgm-spt-n accent">[tool_use, tool_use, …]</div>
    <span class="dgm-spt-arr">→</span>
    <div class="dgm-spt-n blue">Run each (validate, budget, idempotent, wrap)</div>
    <span class="dgm-spt-arr">→</span>
    <div class="dgm-spt-n green">One user turn: [tool_result, tool_result, …]</div>
  </div>
</div>


All results for a turn go back together in a single user message, each paired by
`tool_use_id`. Independent tools can run concurrently.

## Build It (wire the phase together)

`code/parallel_tools.py` — defaults to **Claude Opus 5**, composes this phase's pieces:

```python
import anthropic
from concurrent.futures import ThreadPoolExecutor
client = anthropic.Anthropic()

# schemas() / dispatch() from lesson 01; validate() from 02; ok()/err() from 03.
def run_call(call):
    err_msg = validate(call.input, SCHEMA_BY_NAME[call.name])
    if err_msg:
        return err(call.id, err_msg)
    try:
        return ok(call.id, dispatch(call.name, call.input))
    except Exception as e:
        return err(call.id, str(e))

def step(messages, tools):
    msg = client.messages.create(model="claude-opus-5", max_tokens=1024,
                                 tools=tools, messages=messages)
    messages.append({"role": "assistant", "content": msg.content})
    calls = [b for b in msg.content if b.type == "tool_use"]
    if not calls:
        return messages, "".join(b.text for b in msg.content if b.type == "text")
    with ThreadPoolExecutor() as pool:                 # independent tools run in parallel
        results = list(pool.map(run_call, calls))
    messages.append({"role": "user", "content": results})
    return messages, None
```

Each result reuses your hand-built validation and wrapping. Parallelism is safe
*because* side-effecting tools are idempotent (lesson 04).

## Use It

This is the production tool loop: pass `tools=schemas()`, collect every `tool_use`, run
them in parallel when they're independent, and return all `tool_result` blocks in one
user turn. The SDK also supports forcing a specific tool via `tool_choice` for structured
output.

## Ship It

[`code/parallel_tools.py`](../../07-sdk-parallel-tools/code/parallel_tools.py) — an SDK tool
loop with parallel dispatch composing the whole phase.

## Check Yourself

**Q1.** A turn has three `tool_use` blocks. You should…

- A) run only the first
- B) run all three and return three `tool_result` blocks in one user turn
- C) error
- D) run them across three separate turns

<details><summary>Answer</summary>B — answer every requested call together.</details>

**Q2.** What makes parallel tool execution safe?

- A) luck
- B) idempotent side-effecting tools (lesson 04) plus independent inputs
- C) a bigger model
- D) lower temperature

<details><summary>Answer</summary>B — idempotency guards against overlap/retry
hazards.</details>

**Challenge.** Add `tool_choice={"type": "tool", "name": "extract"}` to force the model to
produce a structured object via a single tool — the robust structured-output path from
Phase 1 lesson 07.

## Related

- Builds on: lessons [01](../../01-schemas-and-dispatch/docs/en.md)–[06](../../06-tool-descriptions/docs/en.md)
- Next: [A tool registry & discovery layer](../../08-tool-registry/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
