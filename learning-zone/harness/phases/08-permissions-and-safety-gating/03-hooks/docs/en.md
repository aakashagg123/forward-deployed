# Pre/Post tool-use hooks

> **Motto** — Hooks let deterministic code run before and after every tool call — no prompt required.

*Part of Phase 08 — Permissions & Safety Gating.*

## The Problem

Some rules must be *guaranteed*, not merely requested of the model: "never edit `.env`",
"run the linter after every write", "redact secrets from output". You can't trust a prompt
for these (Phase 0 lesson 03). **Hooks** are the mechanism: deterministic scripts the harness
runs *around* each tool call. A PreToolUse hook can block or modify a call. A PostToolUse
hook can react to the result.

## The Concept

<style>
.dgm-hk{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-hk-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-hk h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-hk-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-hk-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-hk-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-hk-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-hk-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-hk-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-hk-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-hk-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-hk-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-hk{padding:20px 16px 18px}.dgm-hk-row{flex-direction:column}}
.dgm-hk-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-hk-branches{display:grid;grid-template-columns:repeat(1,1fr);gap:10px}
.dgm-hk-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-hk-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-hk-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-hk-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-hk-b.accent h6{color:#0d5c0d}
.dgm-hk-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-hk-b.blue h6{color:#0550ae}
.dgm-hk-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-hk-b.green h6{color:#1a614f}
.dgm-hk-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-hk-b.red h6{color:#82061e}
.dgm-hk-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-hk-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-hk{padding:20px 16px 18px}.dgm-hk-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-hk">
  <span class="dgm-hk-chip">Two hook points bracket every tool call</span>
  <h4>PreToolUse can block or modify; PostToolUse can augment the result</h4>
  <p class="dgm-hk-sub">PreToolUse runs before the tool ever executes — it's the only hook that can stop it.</p>
  <div class="dgm-hk-row">
    <div class="dgm-hk-n neutral">Tool call</div>
    <span class="dgm-hk-arr">→</span>
    <div class="dgm-hk-n accent">PreToolUse hook(s)</div>
  </div>
  <div class="dgm-hk-branches">
    <div class="dgm-hk-b red">
      <h6>Block</h6>
      <p>Denied</p>
    </div>
  </div>
  <div class="dgm-hk-row">
    <div class="dgm-hk-n blue">Allow / modify → execute tool</div>
    <span class="dgm-hk-arr">→</span>
    <div class="dgm-hk-n accent">PostToolUse hook(s)</div>
    <span class="dgm-hk-arr">→</span>
    <div class="dgm-hk-n green">Result (maybe augmented)</div>
  </div>
</div>


Pre-hooks gate and rewrite inputs. Post-hooks observe and augment outputs — for example,
injecting lint violations into context.

## Build It

`code/hooks.py` — a hook runner with pre (can block) and post (can augment) phases:

```python
class HookRunner:
    def __init__(self):
        self.pre, self.post = [], []      # callables

    def on_pre(self, fn): self.pre.append(fn)
    def on_post(self, fn): self.post.append(fn)

    def call(self, tool, args, execute):
        for hook in self.pre:
            verdict = hook(tool, args)     # return ("deny", msg) or ("allow", args)
            if verdict[0] == "deny":
                return f"blocked: {verdict[1]}"
            args = verdict[1]
        result = execute(tool, args)
        for hook in self.post:
            result = hook(tool, args, result)
        return result
```

```python
hr = HookRunner()
hr.on_pre(lambda t, a: ("deny", ".env is protected")
          if a.get("path", "").endswith(".env") else ("allow", a))
hr.on_post(lambda t, a, r: r + "  [lint: ok]" if t == "write" else r)
print(hr.call("write", {"path": ".env"}, execute=lambda t, a: "wrote"))   # blocked
print(hr.call("write", {"path": "app.py"}, execute=lambda t, a: "wrote")) # wrote [lint: ok]
```

Pre-hooks are your enforcement layer — they block `.env`. Post-hooks are your reaction
layer — they run the linter and inject its output. Both are deterministic. Neither needs
a prompt.

## Use It

This is the Claude Code **hooks** system in `settings.json` (`PreToolUse`, `PostToolUse`,
and more). It's exactly where the `.env` guard (Phase 0), the tool budgets (Phase 3), and
the egress guard (Phase 7) plug in. Codex offers comparable lifecycle hooks. A PostToolUse
linter hook that injects violations into context is the canonical "lint as a teaching tool"
pattern.

## Ship It

[`code/hooks.py`](../../03-hooks/code/hooks.py) — a pre/post tool-use hook runner.

## Check Yourself

**Q1.** What can a PreToolUse hook do that a prompt instruction can't?

- A) be polite
- B) deterministically block or rewrite a call before it runs
- C) use fewer tokens
- D) nothing

<details><summary>Answer</summary>B — guaranteed enforcement, not persuasion.</details>

**Q2.** A linter that injects violations into context after a write is a…

- A) PreToolUse hook
- B) PostToolUse hook
- C) permission mode
- D) prompt

<details><summary>Answer</summary>B — it reacts to the result.</details>

**Challenge.** Add a PostToolUse hook that redacts anything matching an API-key pattern from
tool output. This previews the Phase 17 secret redaction lesson.

## Related

- Builds on: [Permission modes](../../01-permission-modes/docs/en.md); Phase 0 — [.env hook](../../../00-setup-and-tooling/03-secrets-and-env/docs/en.md)
- Next: [Human-in-the-loop approval flows](../../04-approvals/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
