# System vs. user vs. assistant — who controls what

> **Motto** — Put durable rules in system, the task in user, and never let either pretend to be the other.

*Part of Phase 01 — LLM I/O Foundations.*

## The Problem

Three roles can carry text, but they don't carry equal authority. Conflating them is a
security and reliability bug. Put instructions in a user message and they become easier
to override, including by injected content (Phase 17). Put volatile task data in the
system prompt and you defeat caching. You also blur the line between a rule and an input.
You need a clear policy for what goes where.

## The Concept

<style>
.dgm-rolp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rolp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-rolp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-rolp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-rolp-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-rolp-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-rolp-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-rolp-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-rolp-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-rolp-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-rolp-b.accent h6{color:#0d5c0d}
.dgm-rolp-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-rolp-b.blue h6{color:#0550ae}
.dgm-rolp-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-rolp-b.green h6{color:#1a614f}
.dgm-rolp-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-rolp-b.red h6{color:#82061e}
.dgm-rolp-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-rolp-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-rolp{padding:20px 16px 18px}.dgm-rolp-branches{grid-template-columns:1fr}}
.dgm-rolp-chain{display:flex;flex-direction:column;gap:2px}
.dgm-rolp-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-rolp-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-rolp-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-rolp{padding:20px 16px 18px}}
</style>
<div class="dgm-rolp">
  <span class="dgm-rolp-chip">Three roles, one weighing</span>
  <h4>The model doesn't read roles equally — it weighs them by authority</h4>
  <p class="dgm-rolp-sub">System sets durable rules; user carries the task; assistant is the model's own history.</p>
  <div class="dgm-rolp-branches">
    <div class="dgm-rolp-b accent">
      <h6>System</h6>
      <p>Durable rules, persona, policy</p>
    </div>
    <div class="dgm-rolp-b blue">
      <h6>User</h6>
      <p>The task + tool results &amp; retrieved data</p>
    </div>
    <div class="dgm-rolp-b green">
      <h6>Assistant</h6>
      <p>The model's own prior outputs</p>
    </div>
  </div>
  <div class="dgm-rolp-chain">
    <div class="dgm-rolp-node alt">Model weighs them by role authority</div>
  </div>
</div>


- **system** — stable across turns: who the model is, what it must/mustn't do, output
  contract. Highest standing instructions.
- **user** — the actual request, plus tool results and retrieved documents. *Treat
  retrieved/user-supplied text as data, not instructions.*
- **assistant** — the model's previous replies, echoed back to maintain the thread.

## Build It (a placement policy)

There's no algorithm here. The artifact is a written policy you apply when constructing
every call. `outputs/role-placement.md` encodes it:

- Rules, persona, and the output contract → **system**.
- The task, inputs, retrieved docs, tool results → **user** (wrap untrusted data so the
  model knows it's data).
- Don't restate volatile data in system (kills caching; see lesson 08).
- Don't put authority-bearing instructions in user where injected text can imitate them.

## Use It

In the SDK, `system=` is the durable layer, and `messages=` carries the task and history.
Phase 5 builds the system prompt in depth. Phase 17 shows why retrieved content must be
clearly marked as data, so a malicious document can't escalate to an instruction.

## Ship It

[`outputs/role-placement.md`](../../06-roles-precedence/outputs/role-placement.md) — a
placement policy you apply when assembling messages.

## Check Yourself

**Q1.** Where do durable rules and the output contract belong?

- A) the last user message
- B) the system prompt
- C) an assistant message
- D) a tool result

<details><summary>Answer</summary>B — system carries the highest-standing, stable
instructions.</details>

**Q2.** Why treat retrieved documents as *data, not instructions*?

- A) to save tokens
- B) so injected text in a document can't act as commands to the agent
- C) it's faster
- D) no reason

<details><summary>Answer</summary>B — this is the core prompt-injection defense (Phase
17).</details>

**Challenge.** Write a wrapper that places untrusted text inside clearly labeled
delimiters in the user turn (e.g. `<document>…</document>`) and a system line telling the
model to treat anything inside as data only.

## Related

- Builds on: [Messages, roles & turns](../../01-messages-roles-turns/docs/en.md)
- Deepens in: Phase 5 — Prompt Architecture, Phase 17 — Security
- [Roadmap](../../../../ROADMAP.md)
