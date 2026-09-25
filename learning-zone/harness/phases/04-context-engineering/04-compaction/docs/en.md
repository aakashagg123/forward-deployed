# Compaction & summarization across turns

> **Motto** — When history won't fit, replace it with a summary that preserves the facts that matter.

*Part of Phase 04 — Context Engineering.*

## The Problem

Truncation (lesson 03) keeps the conversation valid, but it *loses* the dropped content.
Sometimes the agent needed a decision made 30 turns ago. Compaction is the better move:
summarize the old portion into a compact note that covers key decisions, open threads, and
file state. Keep that note instead, so the agent remembers the gist without the full
transcript. This is what "compacting conversation…" means in a long Claude Code / Codex
session.

## The Concept

<style>
.dgm-comp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-comp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-comp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-comp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-comp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-comp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-comp-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-comp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-comp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-comp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-comp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-comp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-comp{padding:20px 16px 18px}.dgm-comp-row{flex-direction:column}}
</style>
<div class="dgm-comp">
  <span class="dgm-comp-chip">Summarize instead of dropping</span>
  <h4>Old turns become one synopsis note, not zero turns</h4>
  <p class="dgm-comp-sub">Compaction keeps the gist where truncation would have thrown it away entirely.</p>
  <div class="dgm-comp-row">
    <div class="dgm-comp-n neutral">Old turns</div>
    <span class="dgm-comp-arr">→</span>
    <div class="dgm-comp-n accent">Summarize → synopsis note</div>
    <span class="dgm-comp-arr">→</span>
    <div class="dgm-comp-n green">History = [synopsis] + recent turns</div>
  </div>
</div>


The synopsis must capture decisions made, the current goal or plan, files touched, and
unresolved questions. It should record the working state, not a blow-by-blow account.

## Build It

`code/compaction.py` — compaction with a pluggable summarizer (a stub here; the model in
production):

```python
def compact(messages, est, max_tokens, summarize, keep_recent=4):
    def size(ms): return sum(est(str(m.get("content",""))) for m in ms)
    if size(messages) <= max_tokens:
        return messages
    old, recent = messages[:-keep_recent], messages[-keep_recent:]
    synopsis = summarize(old)                       # model call in production
    note = {"role": "user",
            "content": f"[summary of earlier conversation]\n{synopsis}"}
    return [note] + recent

def stub_summarize(old):
    decisions = [m["content"] for m in old if m["role"] == "assistant"]
    return f"{len(old)} earlier messages. Key points: " + " | ".join(decisions[:3])
```

```python
est = lambda s: max(1, len(s)//4)
msgs = [{"role": "assistant", "content": f"decided thing {i}"} for i in range(20)]
out = compact(msgs, est, max_tokens=50, summarize=stub_summarize)
print(out[0]["content"][:40], "…")     # the synopsis replaces the bulk
```

In production `summarize` is a model call with a prompt like *"Summarize the decisions,
current plan, files changed, and open questions."* The structure of the synopsis is what
makes compaction lossy-but-useful instead of lossy-and-harmful.

## Use It

This is exactly the auto-compaction in **Claude Code / Codex**. When the window fills,
the tool summarizes the earlier conversation and continues from the synopsis plus recent
turns. Knowing this, state important decisions explicitly so they survive compaction, and
`/clear` or start fresh when you switch tasks.

## Ship It

[`code/compaction.py`](../../04-compaction/code/compaction.py) — history compaction with a
pluggable summarizer.

## Check Yourself

**Q1.** Compaction beats plain truncation because…

- A) it's faster
- B) it preserves the gist (decisions, plan, files) instead of losing it
- C) it uses fewer tokens always
- D) it never calls the model

<details><summary>Answer</summary>B — summary retains working state.</details>

**Q2.** A good synopsis captures…

- A) every message verbatim
- B) decisions, current plan, files touched, open questions
- C) only the last message
- D) the system prompt

<details><summary>Answer</summary>B — the working state, not a transcript.</details>

**Challenge.** Make compaction *recursive*: when the synopsis-plus-recent still overflows,
summarize again, and verify facts from the first summary survive.

## Related

- Builds on: [Truncation](../../03-truncation/docs/en.md)
- Next: [Injecting files & retrieved context safely](../../05-injecting-context/docs/en.md)
- Deepens in: Phase 9 — Memory & Persistence
- [Roadmap](../../../../ROADMAP.md)
