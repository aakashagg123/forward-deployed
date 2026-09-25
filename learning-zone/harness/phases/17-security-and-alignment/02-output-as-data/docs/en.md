# Treating model output as data, never control flow

> **Motto** — The model proposes; the harness disposes — model text is a request, not a command.

*Part of Phase 17 — Security & Alignment.*

## The Problem

The deepest injection defense is architectural: **never let model output directly drive
privileged control flow**. If the harness runs `eval()` on the model's text, or runs
whatever shell string it emits, an injected instruction becomes code execution. Instead,
treat model output as *data*. The harness validates it against an allowlist of permitted
actions before anything happens. This is the structural reason the permission layer
(Phase 8) exists.

## The Concept

<style>
.dgm-oad{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-oad-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-oad h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-oad-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-oad-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-oad-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-oad-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-oad-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-oad-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-oad-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-oad-b.accent h6{color:#0d5c0d}
.dgm-oad-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-oad-b.blue h6{color:#0550ae}
.dgm-oad-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-oad-b.green h6{color:#1a614f}
.dgm-oad-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-oad-b.red h6{color:#82061e}
.dgm-oad-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-oad-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-oad{padding:20px 16px 18px}.dgm-oad-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-oad">
  <span class="dgm-oad-chip">Parse the output before you ever act on it</span>
  <h4>A proposed action only runs if it's on the allowlist and its args validate</h4>
  <p class="dgm-oad-sub">Model output is untrusted the same way user input is — it's parsed, checked, then maybe run.</p>
  <div class="dgm-oad-q">Model output (untrusted) → parse into a proposed action — action ∈ allowlist &amp; args valid?</div>
  <div class="dgm-oad-branches">
    <div class="dgm-oad-b green">
      <h6>Yes</h6>
      <p>Execute</p>
    </div>
    <div class="dgm-oad-b red">
      <h6>No</h6>
      <p>Reject — never executed</p>
    </div>
  </div>
</div>


The model can *ask* for any action, but only allowlisted, validated actions run. Injection
can change the *request* but never the *policy*.

## Build It

`code/output_as_data.py` — dispatch model proposals through an allowlist, never `eval`:

```python
ALLOWED = {"read_file", "list_dir"}        # safe, allowlisted actions

def safe_dispatch(proposed_action, args, tools):
    if proposed_action not in ALLOWED:
        return f"denied: '{proposed_action}' is not an allowed action"
    return tools[proposed_action](**args)  # only allowlisted actions ever run

def NEVER_do_this(model_text):
    # eval(model_text)  # ← arbitrary code execution from untrusted text. Never.
    raise RuntimeError("never execute model output as code")
```

```python
tools = {"read_file": lambda path: f"contents of {path}"}
print(safe_dispatch("read_file", {"path": "a.py"}, tools))   # runs
print(safe_dispatch("delete_everything", {}, tools))         # denied — not allowlisted
```

Even if the model is fully hijacked and "decides" to delete everything, `safe_dispatch`
refuses. The action isn't on the allowlist. The policy lives in the harness, not in the
model's text.

## Use It

This is why Claude Code and Codex route every model-requested action through the permission
system (Phase 8) and typed tools (Phase 3), rather than executing free-form text. The model
can request an action, but an allowlist, validation, and a permission gate decide whether it
runs. The rule to internalize: **model output is data**. Treat it as untrusted input to your
dispatcher, never as code.

## Ship It

[`code/output_as_data.py`](../../02-output-as-data/code/output_as_data.py) — an allowlisted
dispatcher (the output-as-data pattern).

## Check Yourself

**Q1.** Why must model output never drive control flow directly?

- A) it's slow
- B) an injected instruction would become real action/code execution
- C) it's untidy
- D) no reason

<details><summary>Answer</summary>B — output-as-control-flow turns injection into
exploitation.</details>

**Q2.** What decides whether a model-requested action runs?

- A) the model's confidence
- B) the harness: allowlist + arg validation + permission gate
- C) the prompt
- D) nothing

<details><summary>Answer</summary>B — policy lives in the harness, not the text.</details>

**Challenge.** Combine with Phase 8: route `safe_dispatch` through the `PermissionGate` so an
allowlisted-but-risky action (e.g. `write_file`) still prompts for confirmation.

## Related

- Builds on: [Prompt injection](../../01-prompt-injection/docs/en.md); Phase 8 — [Permissions](../../../08-permissions-and-safety-gating/01-permission-modes/docs/en.md)
- Next: [Data exfiltration & egress guards](../../03-exfiltration/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
