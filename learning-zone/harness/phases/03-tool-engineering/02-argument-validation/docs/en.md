# Argument validation & JSON-schema enforcement

> **Motto** — The model proposes arguments; the harness proves they're valid before running anything.

*Part of Phase 03 — Tool Engineering.*

## The Problem

The model fills in tool arguments from a schema, but it can still get them wrong: a
missing required field, a string where a number belongs, a value outside an allowed set.
Call the function anyway and you get a Python traceback, or worse, a silently wrong
action. Validate against the schema first, and a bad call becomes a clean message the
model can fix.

## The Concept

A small JSON-Schema subset covers most tool inputs: `type`, `required`, `enum`, and nested
`properties`.

<style>
.dgm-av{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-av-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-av h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-av-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-av-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-av-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-av-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-av-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-av-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-av-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-av-b.accent h6{color:#0d5c0d}
.dgm-av-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-av-b.blue h6{color:#0550ae}
.dgm-av-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-av-b.green h6{color:#1a614f}
.dgm-av-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-av-b.red h6{color:#82061e}
.dgm-av-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-av-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-av{padding:20px 16px 18px}.dgm-av-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-av">
  <span class="dgm-av-chip">Validate before you run, not after</span>
  <h4>Bad args become a typed error, not a stack trace</h4>
  <p class="dgm-av-sub">The model can read a typed validation error and correct itself next turn.</p>
  <div class="dgm-av-q">Model args valid vs. schema?</div>
  <div class="dgm-av-branches">
    <div class="dgm-av-b green">
      <h6>Yes</h6>
      <p>Run tool</p>
    </div>
    <div class="dgm-av-b red">
      <h6>No</h6>
      <p>Typed error → model</p>
    </div>
  </div>
</div>


## Build It

`code/validate.py` — a minimal schema validator returning a precise error or `None`:

```python
TYPES = {"string": str, "number": (int, float), "integer": int,
         "boolean": bool, "object": dict, "array": list}

def validate(args, schema):
    if schema.get("type") == "object":
        for key in schema.get("required", []):
            if key not in args:
                return f"missing required field {key!r}"
        for key, spec in schema.get("properties", {}).items():
            if key in args:
                err = _check(args[key], spec, key)
                if err:
                    return err
    return None

def _check(value, spec, path):
    t = spec.get("type")
    if t and not isinstance(value, TYPES[t]):
        return f"{path}: expected {t}, got {type(value).__name__}"
    if "enum" in spec and value not in spec["enum"]:
        return f"{path}: {value!r} not in {spec['enum']}"
    return None
```

```python
schema = {"type": "object",
          "properties": {"unit": {"type": "string", "enum": ["c", "f"]},
                         "temp": {"type": "number"}},
          "required": ["temp"]}
print(validate({"temp": 20, "unit": "c"}, schema))   # None (valid)
print(validate({"unit": "k"}, schema))               # missing required 'temp'
print(validate({"temp": "hot"}, schema))             # temp: expected number, got str
```

The error strings are written for the *model* to read. Name the field and what was
wrong, so it self-corrects in one turn.

## Use It

Providers do some validation, but you should validate at the dispatch boundary too. It
adds defense in depth, and you control the wording of the message for recovery. This is
the same errors-are-data principle from the agent loop, applied to arguments.

## Ship It

[`code/validate.py`](../../02-argument-validation/code/validate.py) — a minimal JSON-schema
argument validator.

## Check Yourself

**Q1.** A model passes a string for a numeric field. Validation should…

- A) crash the loop
- B) return a typed error naming the field so the model retries correctly
- C) coerce silently
- D) ignore it

<details><summary>Answer</summary>B — clear, model-readable errors enable
self-correction.</details>

**Q2.** Why validate even though the provider checks the schema?

- A) it's required
- B) defense in depth, and you control the error wording for recovery
- C) speed
- D) you shouldn't

<details><summary>Answer</summary>B — validate at your boundary too.</details>

**Challenge.** Add `minimum`/`maximum` for numbers and `minLength` for strings to the
validator.

## Related

- Builds on: [Tool schemas & dispatch](../../01-schemas-and-dispatch/docs/en.md)
- Next: [Tool results, errors & the feedback channel](../../03-results-and-errors/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
