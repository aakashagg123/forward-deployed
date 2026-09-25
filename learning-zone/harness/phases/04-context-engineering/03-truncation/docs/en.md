# Truncation that doesn't break tool calls

> **Motto** — Trim oldest-first, but never split a tool_use from its tool_result.

*Part of Phase 04 — Context Engineering.*

## The Problem

When history exceeds budget, the obvious fix is to drop the oldest messages. But a coding
agent's history is full of `tool_use`/`tool_result` pairs. The API rejects a conversation
where a `tool_use` has no matching `tool_result` (Phase 2 lesson 04). Naive truncation
produces exactly that invalid state, so trimming must respect pairing.

## The Concept

<style>
.dgm-trunc{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-trunc-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-trunc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-trunc-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-trunc-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-trunc-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-trunc-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-trunc-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-trunc-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-trunc-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-trunc-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-trunc-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-trunc{padding:20px 16px 18px}.dgm-trunc-row{flex-direction:column}}
</style>
<div class="dgm-trunc">
  <span class="dgm-trunc-chip">Drop whole pairs, never half a turn</span>
  <h4>Truncation keeps system and recent turns, drops oldest complete pairs only</h4>
  <p class="dgm-trunc-sub">Dropping half a user/assistant pair would leave a dangling tool_use with no result.</p>
  <div class="dgm-trunc-row">
    <div class="dgm-trunc-n red">History over budget</div>
    <span class="dgm-trunc-arr">→</span>
    <div class="dgm-trunc-n accent">Keep system + recent turns</div>
    <span class="dgm-trunc-arr">→</span>
    <div class="dgm-trunc-n blue">Drop oldest complete pairs only</div>
    <span class="dgm-trunc-arr">→</span>
    <div class="dgm-trunc-n green">Result: valid, smaller history</div>
  </div>
</div>


Rule: drop whole exchanges (a user/assistant turn plus any tool pair it spawned), never a
half-pair. Always keep the most recent turns intact.

## Build It

`code/truncate.py` — pair-aware truncation:

```python
def truncate(messages, max_tokens, est, keep_recent=4):
    """Drop oldest complete exchanges until under budget; never split tool pairs."""
    msgs = list(messages)
    def size(ms): return sum(est(str(m.get("content", ""))) for m in ms)
    while size(msgs) > max_tokens and len(msgs) > keep_recent:
        # find the end of the oldest exchange (advance past any tool messages)
        cut = 1
        while cut < len(msgs) - keep_recent and msgs[cut]["role"] == "tool":
            cut += 1
        del msgs[:cut]                              # drop a whole leading exchange
    return msgs
```

```python
est = lambda s: max(1, len(s)//4)
msgs = [{"role": "user", "content": "x"*400} for _ in range(10)]
print(len(truncate(msgs, max_tokens=200, est=est)))   # trimmed, recent kept
```

The loop removes leading exchanges as a unit, so a `tool_use` and its `tool_result` are
always dropped together — the conversation stays valid.

## Use It

When a session gets long, **Claude Code / Codex** don't just hard-cut — they compact
(next lesson). But the invariant is the same: the running message list they send must keep
every tool call paired. If you ever build a custom loop on the Agent SDK, this pair-aware
trim is the floor under it.

## Ship It

[`code/truncate.py`](../../03-truncation/code/truncate.py) — pair-aware history truncation.

## Check Yourself

**Q1.** Why can't you drop a single `tool_use` message to save tokens?

- A) it's small
- B) its `tool_result` would be orphaned and the API rejects the conversation
- C) it's recent
- D) you can

<details><summary>Answer</summary>B — pairs must stay together (Phase 2 L4).</details>

**Q2.** What does pair-aware truncation always preserve?

- A) the longest messages
- B) the most recent turns and valid tool pairing
- C) random messages
- D) only the system prompt

<details><summary>Answer</summary>B — recent + valid structure.</details>

**Challenge.** Make truncation *summarize* the dropped exchanges into one note instead of
deleting them outright — the bridge to compaction (next lesson).

## Related

- Builds on: [Message assembly](../../02-message-assembly/docs/en.md), Phase 2 L4 history
- Next: [Compaction & summarization](../../04-compaction/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
