# Long-term memory & retrieval

> **Motto** — Long-term memory is a store you write facts to and retrieve the relevant few from.

*Part of Phase 09 — Memory & Persistence.*

## The Problem

The scratchpad (lesson 01) dies with the session. Persisted sessions (lesson 02) are
per-conversation. Some knowledge should outlive both: "this project uses pnpm," "the auth
flow lives in `auth/`," "we decided against Redis." Long-term memory is a durable store.
The agent writes such facts to it and *retrieves the relevant ones from* it on later tasks,
without loading the entire memory into context.

## The Concept

<style>
.dgm-ltm{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ltm-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ltm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ltm-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ltm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-ltm-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-ltm-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-ltm-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-ltm-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-ltm-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-ltm-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-ltm-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-ltm{padding:20px 16px 18px}.dgm-ltm-row{flex-direction:column}}
</style>
<div class="dgm-ltm">
  <span class="dgm-ltm-chip">Write once, retrieve by relevance</span>
  <h4>remember() writes to a store; a new task retrieves the top-k relevant facts</h4>
  <p class="dgm-ltm-sub">Retrieval is scoped to what's relevant to the current query, not the whole store.</p>
  <div class="dgm-ltm-row">
    <div class="dgm-ltm-n accent">remember(fact)</div>
    <span class="dgm-ltm-arr">→</span>
    <div class="dgm-ltm-n blue">Memory store</div>
  </div>
  <div class="dgm-ltm-row" style="margin-top:8px">
    <div class="dgm-ltm-n neutral">New task / query</div>
    <span class="dgm-ltm-arr">→</span>
    <div class="dgm-ltm-n blue">Retrieve top-k relevant facts</div>
    <span class="dgm-ltm-arr">→</span>
    <div class="dgm-ltm-n green">Inject into context</div>
  </div>
</div>


Write is append; read is *retrieval*, ranked by relevance, so context stays lean even as
the store grows. This lesson uses lexical ranking. Phase 13 covers embeddings.

## Build It

`code/long_term.py` — an append-and-retrieve memory store:

```python
import json, os

class LongTermMemory:
    def __init__(self, path):
        self.path = path
        self.facts = json.load(open(path)) if os.path.exists(path) else []

    def remember(self, fact, tags=()):
        self.facts.append({"fact": fact, "tags": list(tags)})
        json.dump(self.facts, open(self.path, "w"))
        return "remembered"

    def retrieve(self, query, k=3):
        q = set(query.lower().split())
        def score(e):
            words = set(e["fact"].lower().split()) | set(e["tags"])
            return len(q & words)
        ranked = sorted(self.facts, key=score, reverse=True)
        return [e["fact"] for e in ranked[:k] if score(e) > 0]
```

```python
import tempfile
m = LongTermMemory(tempfile.mktemp(suffix=".json"))
m.remember("This project uses pnpm, not npm.", tags=["build"])
m.remember("Auth flow lives in auth/.", tags=["auth"])
print(m.retrieve("how do I build"))     # ['This project uses pnpm, not npm.']
```

The agent calls `remember` when it learns something durable. The harness calls `retrieve`
to surface the few relevant facts per task — not the whole store.

## Use It

This is the pattern behind project memory that persists beyond one chat: a `knowledge.md`
(the append-only system of record from the harness principles), per-user memory, or a
dedicated **memory MCP server** (lesson 05) that Claude Code / Codex query each session.
The key discipline: retrieve relevant facts. Don't dump the whole memory into `CLAUDE.md`.

## Ship It

[`code/long_term.py`](../../03-long-term-memory/code/long_term.py) — an append-and-retrieve
long-term memory store.

## Check Yourself

**Q1.** Why *retrieve* from long-term memory rather than load all of it?

- A) it's faster to load all
- B) the store grows; retrieving the relevant few keeps context lean
- C) the API requires it
- D) no reason

<details><summary>Answer</summary>B — retrieval keeps context small as memory grows.</details>

**Q2.** When should the agent call `remember`?

- A) every turn
- B) when it learns a durable fact worth carrying to future tasks
- C) never
- D) only on errors

<details><summary>Answer</summary>B — persist durable knowledge, not transient
chatter.</details>

**Challenge.** Replace lexical scoring with embedding similarity (Phase 13). Dedupe
near-identical facts on `remember`.

## Related

- Builds on: [Persist & resume](../../02-persist-resume/docs/en.md)
- Next: [Compaction across sessions](../../04-cross-session-compaction/docs/en.md)
- Deepens in: Phase 13 — Retrieval
- [Roadmap](../../../../ROADMAP.md)
