# Tool results, errors & the feedback channel

> **Motto** — A tool result is a message back to the model — shape it so the model can use it.

*Part of Phase 03 — Tool Engineering.*

## The Problem

After a tool runs, its output goes back to the model as a `tool_result`. How you shape
that result determines whether the model uses it well. Huge raw dumps blow the context
budget, unlabeled errors confuse the model, and a missing `is_error` flag makes failures
look like success. The feedback channel needs structure.

## The Concept

A well-formed result carries: the `tool_use_id` it answers, a concise `content`, and an
`is_error` flag.

<style>
.dgm-rae{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rae-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-rae h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-rae-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-rae-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-rae-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-rae-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-rae-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-rae-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-rae-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-rae-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-rae-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-rae{padding:20px 16px 18px}.dgm-rae-row{flex-direction:column}}
</style>
<div class="dgm-rae">
  <span class="dgm-rae-chip">Every result gets the same envelope</span>
  <h4>Wrap, then budget — a huge result never reaches the model whole</h4>
  <p class="dgm-rae-sub">id + content + is_error is the same shape whether the tool succeeded or not.</p>
  <div class="dgm-rae-row">
    <div class="dgm-rae-n neutral">Tool runs</div>
    <span class="dgm-rae-arr">→</span>
    <div class="dgm-rae-n accent">Wrap: id + content + is_error</div>
    <span class="dgm-rae-arr">→</span>
    <div class="dgm-rae-n blue">Budget: truncate if huge</div>
    <span class="dgm-rae-arr">→</span>
    <div class="dgm-rae-n green">Model</div>
  </div>
</div>


Three rules: pair to the request id, mark errors explicitly, and cap the size (truncate
with a note rather than dumping 50KB).

## Build It

`code/results.py` — wrap outcomes into result blocks with truncation:

```python
MAX_RESULT_CHARS = 4000

def ok(tool_use_id, content):
    return _block(tool_use_id, str(content), is_error=False)

def err(tool_use_id, message):
    return _block(tool_use_id, f"error: {message}", is_error=True)

def _block(tool_use_id, content, is_error):
    if len(content) > MAX_RESULT_CHARS:
        head = content[:MAX_RESULT_CHARS]
        content = f"{head}\n…[truncated {len(content) - MAX_RESULT_CHARS} chars]"
    return {"type": "tool_result", "tool_use_id": tool_use_id,
            "content": content, "is_error": is_error}
```

```python
print(ok("t1", 42))                          # is_error False
print(err("t2", "file not found"))           # is_error True
print(_block("t3", "x" * 5000, False)["content"][-30:])  # …[truncated 1000 chars]
```

The truncation note matters. The model knows output was cut, rather than silently
reasoning over a partial result.

## Use It

These dicts are exactly the `tool_result` content blocks you append as a user turn in the
SDK loop. The `is_error` flag tells the model to treat the content as a failure to
recover from. Truncation here is the first taste of context engineering (Phase 4).

## Ship It

[`code/results.py`](../../03-results-and-errors/code/results.py) — `ok()`/`err()` result
wrappers with size capping.

## Check Yourself

**Q1.** Why set `is_error` on a failed tool result?

- A) logging
- B) so the model treats it as a failure to recover from, not a valid answer
- C) speed
- D) no reason

<details><summary>Answer</summary>B — the flag changes how the model interprets the
content.</details>

**Q2.** A tool returns 50KB. The result wrapper should…

- A) send it all
- B) truncate with a note so the model knows output was cut
- C) drop it
- D) summarize with another model call (always)

<details><summary>Answer</summary>B — cap with a visible truncation marker.</details>

**Challenge.** Add a `summarize_if_over` option that, past a threshold, replaces the body
with a short head+tail slice plus a line count, instead of a hard cut.

## Related

- Builds on: [Argument validation](../../02-argument-validation/docs/en.md)
- Next: [Idempotency & side-effecting tools](../../04-idempotency/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
