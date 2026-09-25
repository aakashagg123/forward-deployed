# Anatomy of a system prompt

> **Motto** — The system prompt is the agent's constitution: role, rules, tools, and output contract.

*Part of Phase 05 — Prompt & Instruction Architecture.*

## The Problem

The system prompt is the highest-authority, most-cached, most-reused text in the harness
(Phase 1 lesson 06, Phase 4 lesson 06). A vague one produces an agent that ignores
constraints, picks the wrong tools, and formats output unpredictably. A bloated one wastes
the cached prefix and buries the rules that matter. You need a structure — known sections,
in a stable order.

## The Concept

<style>
.dgm-spa{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-spa-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-spa h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-spa-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-spa-chain{display:flex;flex-direction:column;gap:2px}
.dgm-spa-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-spa-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-spa-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-spa{padding:20px 16px 18px}}
</style>
<div class="dgm-spa">
  <span class="dgm-spa-chip">Five sections, top to bottom</span>
  <h4>Role, constraints, tools, workflow, output — in an order that matters</h4>
  <p class="dgm-spa-sub">Constraints sit right after role because they bound everything that follows.</p>
  <div class="dgm-spa-chain">
    <div class="dgm-spa-node accent">ROLE — who the agent is</div>
    <div class="dgm-spa-arr">↓</div>
    <div class="dgm-spa-node ">CONSTRAINTS — must / must-never</div>
    <div class="dgm-spa-arr">↓</div>
    <div class="dgm-spa-node ">TOOLS — when to use which</div>
    <div class="dgm-spa-arr">↓</div>
    <div class="dgm-spa-node ">WORKFLOW — how to approach tasks</div>
    <div class="dgm-spa-arr">↓</div>
    <div class="dgm-spa-node alt">OUTPUT CONTRACT — format &amp; tone</div>
  </div>
</div>


Five sections, ordered stable→specific so the prefix caches well: role, hard constraints,
tool guidance, workflow, output contract.

## Build It

The artifact is a structured template, not code. `outputs/system-prompt-template.md`
lays out the five sections with fill-ins and notes on what belongs where. It also notes
what doesn't belong: volatile data never goes here, because it kills caching.

Key rules encoded in the template:

- **Role** in one or two sentences; concrete, not flowery.
- **Constraints** as imperatives ("Never edit `.env`. Always run tests before claiming
  done.") — these are the lines the model must obey.
- **Tools**: when to reach for each, when *not* to (overlap disambiguation, Phase 3 L6).
- **Workflow**: the default approach (e.g. plan → act → verify).
- **Output contract**: format, length, tone — the response shape downstream code expects.

## Use It

This *is* the system prompt that **Claude Code / Codex** ship, plus your additions. The
parts you control are layered in through project memory (`CLAUDE.md` / `AGENTS.md`, next
lesson) and output styles. Knowing the anatomy tells you where your instruction belongs. A
hard rule goes in constraints, and ideally also becomes a hook (Phase 8). A formatting
preference goes in the output contract.

## Ship It

[`outputs/system-prompt-template.md`](../../01-system-prompt-anatomy/outputs/system-prompt-template.md)
— a five-section system-prompt template.

## Check Yourself

**Q1.** Why keep volatile data out of the system prompt?

- A) it's untidy
- B) the system prompt is the cached prefix; changing it invalidates the cache (Phase 1 L8)
- C) the API forbids it
- D) no reason

<details><summary>Answer</summary>B — stable system prompt = cache hits.</details>

**Q2.** A hard rule like "never edit .env" belongs in…

- A) the output contract
- B) the constraints section (and ideally also a hook)
- C) the workflow
- D) a user message

<details><summary>Answer</summary>B — constraints carry the must/must-never
rules.</details>

**Challenge.** Take a rambling system prompt and refactor it into the five sections; note
which lines were redundant and could be deleted.

## Related

- Builds on: Phase 1 — [Roles & precedence](../../../01-llm-io-foundations/06-roles-precedence/docs/en.md)
- Next: [Memory files (CLAUDE.md / AGENTS.md)](../../02-memory-files/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
