# Compaction across sessions

> **Motto** — Distill finished sessions into durable lessons — keep the insight, drop the transcript.

*Part of Phase 09 — Memory & Persistence.*

## The Problem

In-session compaction (Phase 4 lesson 04) shrinks one conversation. But across many
sessions you accumulate transcripts you'll never re-read. They still contain hard-won
lessons, such as "the flaky test is a timing issue" or "don't bump that dep." Cross-session
compaction extracts those lessons into long-term memory (lesson 03). The *knowledge*
persists while the raw transcripts can be archived or discarded.

## The Concept

<style>
.dgm-csc{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-csc-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-csc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-csc-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-csc-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-csc-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-csc-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-csc-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-csc-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-csc-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-csc-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-csc-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-csc{padding:20px 16px 18px}.dgm-csc-row{flex-direction:column}}
.dgm-csc-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-csc-branches{display:grid;grid-template-columns:repeat(1,1fr);gap:10px}
.dgm-csc-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-csc-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-csc-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-csc-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-csc-b.accent h6{color:#0d5c0d}
.dgm-csc-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-csc-b.blue h6{color:#0550ae}
.dgm-csc-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-csc-b.green h6{color:#1a614f}
.dgm-csc-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-csc-b.red h6{color:#82061e}
.dgm-csc-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-csc-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-csc{padding:20px 16px 18px}.dgm-csc-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-csc">
  <span class="dgm-csc-chip">A finished session leaves a lesson, not a transcript</span>
  <h4>Extract symptom→fix pairs into knowledge.md; archive or discard the rest</h4>
  <p class="dgm-csc-sub">The next session reads knowledge.md, not the raw transcript of every prior run.</p>
  <div class="dgm-csc-row">
    <div class="dgm-csc-n neutral">Finished session transcript</div>
    <span class="dgm-csc-arr">→</span>
    <div class="dgm-csc-n accent">Extract lessons (symptom → fix)</div>
    <span class="dgm-csc-arr">→</span>
    <div class="dgm-csc-n green">Long-term memory / knowledge.md</div>
  </div>
  <div class="dgm-csc-branches">
    <div class="dgm-csc-b blue">
      <h6>Raw transcript</h6>
      <p>Archive / discard</p>
    </div>
  </div>
</div>


This is the harness-principles "persistent cross-sprint memory": append precise lessons —
symptom, root cause, fix. Write evidence, not vague summaries.

## Build It

`code/distill.py` — distill a session into memory entries:

```python
def distill(transcript, remember):
    """Extract durable lessons from a transcript and write them to memory.
    `extract` is a model call in production; here it's a simple heuristic."""
    lessons = []
    for msg in transcript:
        text = msg.get("content", "")
        if isinstance(text, str) and ("fix:" in text.lower() or "lesson:" in text.lower()):
            lessons.append(text.strip())
    for lesson in lessons:
        remember(lesson, tags=["lesson"])
    return f"distilled {len(lessons)} lesson(s)"
```

```python
saved = []
transcript = [{"role": "assistant", "content": "Fix: the flaky test needs a 200ms wait."},
              {"role": "assistant", "content": "Did some refactoring."}]
print(distill(transcript, remember=lambda f, tags: saved.append(f)))   # distilled 1
print(saved)
```

In production `distill` is a model call ("extract durable lessons as symptom→fix") that
writes to `LongTermMemory` or `knowledge.md`. The transcript can then be archived. The
lesson endures.

## Use It

This is the **memory agent** from the harness-principles pipeline (Phase 10). After a
sprint, it appends precisely worded failure patterns to `knowledge.md`. For a Claude
Code / Codex user, the lightweight version is ending a session by asking the agent to
"append what we learned to `knowledge.md`." The next session then starts smarter without
re-reading old chats.

## Ship It

[`code/distill.py`](../../04-cross-session-compaction/code/distill.py) — a session→memory
distiller.

## Check Yourself

**Q1.** What does cross-session compaction keep, and what does it drop?

- A) keeps the transcript, drops the lessons
- B) keeps the distilled lessons (symptom→fix), drops/archives the raw transcript
- C) keeps everything
- D) drops everything

<details><summary>Answer</summary>B — keep insight, shed transcript.</details>

**Q2.** A good distilled lesson is…

- A) "the session went well"
- B) precise: symptom, root cause, fix
- C) the full transcript
- D) a token count

<details><summary>Answer</summary>B — evidence, not vague summary.</details>

**Challenge.** Make `distill` a real model call that returns structured `{symptom, cause,
fix}` entries. Dedupe against existing memory before writing.

## Related

- Builds on: [Long-term memory](../../03-long-term-memory/docs/en.md); Phase 4 — [Compaction](../../../04-context-engineering/04-compaction/docs/en.md)
- Next: [Use It: a memory MCP server](../../05-memory-mcp/docs/en.md)
- Related: Phase 10 — memory agent / knowledge.md
- [Roadmap](../../../../ROADMAP.md)
