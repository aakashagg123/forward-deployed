# Few-shot & in-context examples that scale

> **Motto** — A couple of well-chosen examples teach format and edge cases better than paragraphs of rules.

*Part of Phase 05 — Prompt & Instruction Architecture.*

## The Problem

Sometimes prose instructions don't land a tricky format or an edge case, and the fix is to
*show* the model: a few input→output examples. But examples cost tokens, and dumping ten of
them bloats the prompt and the cached prefix. The skill is selecting a *small, relevant* set. When you have many examples, pick them
dynamically per query rather than always sending all.

## The Concept

<style>
.dgm-fs{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-fs-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-fs h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-fs-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-fs-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-fs-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-fs-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-fs-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-fs-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-fs-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-fs-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-fs-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-fs{padding:20px 16px 18px}.dgm-fs-row{flex-direction:column}}
</style>
<div class="dgm-fs">
  <span class="dgm-fs-chip">Examples are selected, not fixed</span>
  <h4>The k most relevant examples get prepended as input→output pairs</h4>
  <p class="dgm-fs-sub">Picking examples per query beats a static set baked into the prompt.</p>
  <div class="dgm-fs-row">
    <div class="dgm-fs-n neutral">Query</div>
    <span class="dgm-fs-arr">→</span>
    <div class="dgm-fs-n accent">Select k most relevant examples</div>
    <span class="dgm-fs-arr">→</span>
    <div class="dgm-fs-n blue">Prepend as input → output pairs</div>
    <span class="dgm-fs-arr">→</span>
    <div class="dgm-fs-n green">Model</div>
  </div>
</div>


Two regimes: a fixed handful (2–3) baked into the prompt for a stable task, or dynamic
selection of the top-k examples by similarity to the current input when you have a library.

## Build It

`code/few_shot.py` — a simple selector + formatter (lexical overlap stands in for embeddings,
which arrive in Phase 13):

```python
def select(examples, query, k=2):
    def overlap(ex):
        a, b = set(ex["input"].lower().split()), set(query.lower().split())
        return len(a & b)
    return sorted(examples, key=overlap, reverse=True)[:k]

def format_fewshot(examples, query):
    shots = "\n\n".join(f"Input: {e['input']}\nOutput: {e['output']}" for e in examples)
    return f"{shots}\n\nInput: {query}\nOutput:"
```

```python
ex = [{"input": "add user route", "output": "POST /users"},
      {"input": "delete a product", "output": "DELETE /products/:id"},
      {"input": "list orders", "output": "GET /orders"}]
picked = select(ex, "add product route", k=2)
print(format_fewshot(picked, "add product route"))
```

Selecting the two nearest examples keeps the prompt small while still teaching the pattern.

## Use It

In **Claude Code / Codex**, you rarely hand-write few-shot blocks. Instead, you put a
canonical example in `CLAUDE.md`/`AGENTS.md` — for instance, "a route looks like this" — so
it's applied every turn, and the agent generalizes. The dynamic-selection version is what
you build when a skill needs to choose examples per request. Keep examples few and
relevant: more isn't better once the pattern is clear.

## Ship It

[`code/few_shot.py`](../../05-few-shot/code/few_shot.py) — top-k example selection +
formatting.

## Check Yourself

**Q1.** Why not always include all your examples?

- A) the API caps them
- B) they cost tokens and bloat the cached prefix; a few relevant ones suffice
- C) examples hurt accuracy
- D) no reason

<details><summary>Answer</summary>B — small and relevant beats many.</details>

**Q2.** For a stable, recurring format in your project, the best place for an example is…

- A) every user message
- B) the memory file (CLAUDE.md / AGENTS.md), applied every turn
- C) a separate API
- D) nowhere

<details><summary>Answer</summary>B — bake the canonical example into project memory.</details>

**Challenge.** Swap the lexical overlap for an embedding similarity (forward reference to
Phase 13) and compare which examples each picks.

## Related

- Builds on: [Output contracts](../../04-output-contracts/docs/en.md)
- Next: [Prompt versioning & A/B](../../06-prompt-versioning/docs/en.md)
- Deepens in: Phase 13 — Retrieval
- [Roadmap](../../../../ROADMAP.md)
