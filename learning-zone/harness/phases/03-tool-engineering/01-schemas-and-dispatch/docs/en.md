# Tool schemas & dispatch by hand

> **Motto** — A tool is a function plus a schema that teaches the model how to call it.

*Part of Phase 03 — Tool Engineering. Builds on Phase 2's agent loop.*

## The Problem

The agent loop (Phase 2) dispatched tools from a hand-written dict. Real tools need more.
The model has to *know they exist* and *how to call them*, so each tool carries a
**schema**: name, description, input shape. Dispatch also has to map the model's chosen
name and args to the right Python function. Get the schema wrong and the model calls
tools incorrectly or not at all.

## The Concept

A tool has two halves: the **schema** (sent to the model) and the **implementation** (run
by the harness).

<style>
.dgm-sad{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-sad-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-sad h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-sad-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-sad-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-sad-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-sad-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-sad-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-sad-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-sad-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-sad-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-sad-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-sad{padding:20px 16px 18px}.dgm-sad-row{flex-direction:column}}
</style>
<div class="dgm-sad">
  <span class="dgm-sad-chip">A schema is a contract, dispatch is a lookup</span>
  <h4>The model never calls code directly — it names a tool, dispatch finds the function</h4>
  <p class="dgm-sad-sub">That indirection is what lets you swap implementations without touching the model.</p>
  <div class="dgm-sad-row">
    <div class="dgm-sad-n blue">Schema → model</div>
    <span class="dgm-sad-arr">→</span>
    <div class="dgm-sad-n accent">Model picks name+args</div>
    <span class="dgm-sad-arr">→</span>
    <div class="dgm-sad-n ">Dispatch: name → fn</div>
    <span class="dgm-sad-arr">→</span>
    <div class="dgm-sad-n green">Result → model</div>
  </div>
</div>


The schema is JSON-Schema-shaped: `name`, `description`, `input_schema` with typed
properties and a `required` list.

## Build It

`code/tools.py` — a decorator that registers a function *and* derives its schema, plus a
dispatcher:

```python
REGISTRY = {}

def tool(name, description, schema):
    def deco(fn):
        REGISTRY[name] = {"fn": fn, "schema": {
            "name": name, "description": description, "input_schema": schema}}
        return fn
    return deco

@tool("add", "Add two numbers.",
      {"type": "object",
       "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
       "required": ["a", "b"]})
def add(a, b):
    return a + b

def schemas():
    return [t["schema"] for t in REGISTRY.values()]

def dispatch(name, args):
    entry = REGISTRY.get(name)
    if not entry:
        return f"error: unknown tool {name!r}"
    return str(entry["fn"](**args))
```

```python
print([s["name"] for s in schemas()])   # ['add']
print(dispatch("add", {"a": 2, "b": 3})) # 5
print(dispatch("nope", {}))              # error: unknown tool 'nope'
```

The decorator keeps schema and implementation together, so they never drift apart. That
drift is the #1 source of "the model calls the tool wrong" bugs.

## Use It

This list of schemas is exactly what you pass as `tools=` to `messages.create`. The model
returns `tool_use` blocks naming a tool and its input, and your `dispatch` runs it. You
built the registry the SDK consumes.

## Ship It

[`code/tools.py`](../../01-schemas-and-dispatch/code/tools.py) — a `@tool` decorator,
`schemas()`, and `dispatch()`.

## Check Yourself

**Q1.** What are a tool's two halves?

- A) name and price
- B) the schema sent to the model and the implementation run by the harness
- C) input and output
- D) prompt and response

<details><summary>Answer</summary>B — schema teaches the model; implementation does the
work.</details>

**Q2.** Why keep schema and implementation together (e.g. via a decorator)?

- A) brevity
- B) so they can't drift apart, which causes wrong-call bugs
- C) speed
- D) no reason

<details><summary>Answer</summary>B — co-location prevents schema/impl drift.</details>

**Challenge.** Auto-derive the `input_schema` from the function's type hints so you don't
hand-write it.

## Related

- Builds on: Phase 2 — [The Agent Loop](../../../02-the-agent-loop/01-agent-loop/docs/en.md)
- Next: [Argument validation](../../02-argument-validation/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
