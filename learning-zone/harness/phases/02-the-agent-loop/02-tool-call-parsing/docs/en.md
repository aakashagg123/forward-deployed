# Tool-call parsing & the act step

> **Motto** — The act step turns the model's *words* about an action into a *typed, validated call*.

*Part of Phase 02 — The Agent Loop. Builds on
[The agent loop from scratch](../../01-agent-loop/docs/en.md).*

## The Problem

In lesson 01 the fake model handed us tidy `tool_calls` dicts. Real models don't. They
emit content blocks, or, with weaker models, free-form text like `I'll call add(2, 3)`.
Before the loop can *act*, it has to parse that intent into a structured `(name, args)`
pair it can trust. It also has to reject malformed calls and turn one model message into
possibly several tool invocations. Get this wrong and the loop either crashes on bad
input or executes something the model didn't actually request.

## The Concept

<style>
.dgm-tcp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-tcp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-tcp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-tcp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-tcp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-tcp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-tcp-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-tcp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-tcp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-tcp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-tcp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-tcp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-tcp{padding:20px 16px 18px}.dgm-tcp-row{flex-direction:column}}
.dgm-tcp-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-tcp-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-tcp-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-tcp-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-tcp-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-tcp-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-tcp-b.accent h6{color:#0d5c0d}
.dgm-tcp-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-tcp-b.blue h6{color:#0550ae}
.dgm-tcp-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-tcp-b.green h6{color:#1a614f}
.dgm-tcp-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-tcp-b.red h6{color:#82061e}
.dgm-tcp-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-tcp-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-tcp{padding:20px 16px 18px}.dgm-tcp-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-tcp">
  <span class="dgm-tcp-chip">Validate the shape before you dispatch</span>
  <h4>A model message becomes a list of (name, args) pairs — or an error</h4>
  <p class="dgm-tcp-sub">Invalid shape never reaches a tool; it goes back to the model as a structured error.</p>
  <div class="dgm-tcp-row">
    <div class="dgm-tcp-n neutral">Model message</div>
    <span class="dgm-tcp-arr">→</span>
    <div class="dgm-tcp-n accent">Parse → [(name, args), …]</div>
  </div>
  <div class="dgm-tcp-q">Valid shape?</div>
  <div class="dgm-tcp-branches">
    <div class="dgm-tcp-b red">
      <h6>No</h6>
      <p>Structured error back to model</p>
    </div>
    <div class="dgm-tcp-b green">
      <h6>Yes</h6>
      <p>Dispatch each call → collect results</p>
    </div>
  </div>
</div>


The act step has three jobs: **extract** every tool call from one message, **validate**
each against the tool's schema, and **dispatch** them, in order or in parallel if they're
independent. Parsing failures are data. They go back to the model instead of raising.

## Build It

`code/act.py` — a parser that handles both structured blocks and a text fallback, then
validates argument shape before dispatch:

```python
import json, re

def parse_calls(message):
    """Return [(name, args), ...] from a model message (blocks or text fallback)."""
    if isinstance(message, dict) and message.get("tool_calls"):
        return [(c["name"], c["args"]) for c in message["tool_calls"]]
    text = message if isinstance(message, str) else message.get("text", "")
    calls = []
    for m in re.finditer(r"(\w+)\((\{.*?\})\)", text):      # e.g. add({"a":2,"b":3})
        try:
            calls.append((m.group(1), json.loads(m.group(2))))
        except json.JSONDecodeError:
            pass                                            # skip junk, don't crash
    return calls

def validate(name, args, schema):
    spec = schema.get(name)
    if spec is None:
        return f"error: unknown tool {name!r}"
    missing = [k for k in spec["required"] if k not in args]
    if missing:
        return f"error: {name} missing args {missing}"
    return None                                             # None == valid

def act(message, tools, schema):
    results = []
    for name, args in parse_calls(message):
        err = validate(name, args, schema)
        if err:
            results.append({"name": name, "ok": False, "content": err})
            continue
        try:
            out = str(tools[name](**args))
            results.append({"name": name, "ok": True, "content": out})
        except Exception as e:
            results.append({"name": name, "ok": False, "content": f"error: {e}"})
    return results
```

```python
tools  = {"add": lambda a, b: a + b}
schema = {"add": {"required": ["a", "b"]}}
print(act('add({"a": 2, "b": 3})', tools, schema))
# [{'name': 'add', 'ok': True, 'content': '5'}]
print(act('add({"a": 2})', tools, schema))
# [{'name': 'add', 'ok': False, 'content': 'error: add missing args [\'b\']'}]
```

Notice every path returns a result — valid, unknown tool, missing arg, runtime error.
The loop never sees an exception. The model sees a message it can recover from.

## Use It

With the Anthropic SDK you don't regex anything. Tool calls arrive as typed `tool_use`
content blocks (`block.name`, `block.input`, `block.id`). The validation and dispatch
logic above stays unchanged; only `parse_calls` collapses to
`[b for b in msg.content if b.type == "tool_use"]`. You built the text fallback so you
understand what the SDK saves you from, and why a no-tools model needs it.

## Ship It

[`code/act.py`](../../02-tool-call-parsing/code/act.py) is the artifact — a drop-in
`act(message, tools, schema)` that the Phase 2 agent loop calls in place of its inline
dispatch.

## Check Yourself

**Q1.** Why return a structured error for an unknown tool instead of raising?

- A) It's faster
- B) The model can read the error and pick a valid tool within the same loop
- C) Exceptions aren't allowed in Python
- D) To save tokens

<details><summary>Answer</summary>B — errors are feedback. Raising would kill the loop;
a message lets the model self-correct.</details>

**Q2.** One model message contains two independent tool calls. The act step should…

- A) run only the first
- B) extract and dispatch both, collecting both results
- C) error because only one is allowed
- D) merge them

<details><summary>Answer</summary>B — a single message can request multiple actions;
parse all of them.</details>

**Challenge.** Add an `arg-type` check to `validate` (e.g. `a` must be a number), and
return a message that tells the model the expected type when it's wrong.

## Related

- Builds on: [The agent loop from scratch](../../01-agent-loop/docs/en.md)
- Next: [Termination](../../03-termination/docs/en.md)
- Deepens in: Phase 3 — [Tool Engineering](../../../../ROADMAP.md)
