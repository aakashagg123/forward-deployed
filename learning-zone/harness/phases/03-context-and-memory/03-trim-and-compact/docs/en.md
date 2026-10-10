# Trim and compact

> **Motto** — When history will not fit, shrink it in stages, and never split a tool call from its result.

*Part of Phase 03 — Context and memory.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

A long session overflows the window. The obvious fix is to drop the oldest messages. That fix has a bug.

A coding agent's history is full of pairs. An assistant message holds a `tool_use` block. The next user message holds the matching `tool_result` block. The API rejects a history where one half of a pair is missing. A naive cut can land between the halves.

Dropping text also loses facts. The agent may need a decision it made 30 turns ago. So the harness must do two things: keep the history valid, and keep the gist.

## The Concept

<style>
.dgm-comp{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-comp-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-comp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-comp-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-comp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-comp-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-comp-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-comp-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-comp-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-comp-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-comp-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-comp-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-comp{padding:20px 16px 18px}.dgm-comp-row{flex-direction:column}}
</style>
<div class="dgm-comp">
  <span class="dgm-comp-chip">Cheap stages first, summary last</span>
  <h4>Clear, then drop, then summarize</h4>
  <p class="dgm-comp-sub">Each stage costs more than the last. Every tool_use and tool_result pair stays whole.</p>
  <div class="dgm-comp-row">
    <div class="dgm-comp-n neutral">Old turns</div>
    <span class="dgm-comp-arr">→</span>
    <div class="dgm-comp-n blue">1. Clear old tool output</div>
    <span class="dgm-comp-arr">→</span>
    <div class="dgm-comp-n blue">2. Drop whole turns</div>
    <span class="dgm-comp-arr">→</span>
    <div class="dgm-comp-n accent">3. Summarize → synopsis note</div>
    <span class="dgm-comp-arr">→</span>
    <div class="dgm-comp-n green">History = [synopsis] + recent turns</div>
  </div>
</div>


Work in stages, from cheap to costly.

1. **Clear old tool output.** Replace the body of old `tool_result` blocks with a short note. Keep the blocks, so every pair stays whole.
2. **Drop whole turns.** A turn starts at a real user prompt and includes every tool pair after it. Remove the oldest turns, never single messages.
3. **Compact.** Summarize the old turns into a synopsis. Keep the recent turns word for word.

A good synopsis records decisions, the current plan, files touched and open questions. It is the working state, not a transcript.

## Build It

`code/compaction.py` uses the Anthropic message shape. The key idea is the *turn*. If you only cut at turn boundaries, pairs cannot split.

```python
def turns(messages):
    """Split into turns. Each turn starts at a real prompt and keeps its tool pairs inside."""
    out = []
    for m in messages:
        if is_prompt(m) or not out:
            out.append([])
        out[-1].append(m)
    return out
```

```python
def trim(messages, max_tokens, keep_turns=1):
    """Stage 1: clear old tool output. Stage 2: drop the oldest whole turns."""
    ts = turns(messages)
    flat = lambda xs: [m for t in xs for m in t]
    if size(flat(ts)) > max_tokens:
        ts = [clear_results(t) for t in ts[:-keep_turns]] + ts[-keep_turns:]
    while size(flat(ts)) > max_tokens and len(ts) > keep_turns:
        ts.pop(0)                                    # a whole turn, never a half pair
    return flat(ts)
```

```python
def compact(messages, max_tokens, summarize, keep_turns=2):
    """Replace old turns with a synopsis merged into the first kept prompt."""
    ts = turns(messages)
    if size(messages) <= max_tokens or len(ts) <= keep_turns:
        return messages
    old = [m for t in ts[:-keep_turns] for m in t]
    kept = [m for t in ts[-keep_turns:] for m in t]
    note = f"[summary of earlier conversation]\n{summarize(old)}\n\n"
    first = dict(kept[0], content=note + kept[0]["content"])
    return [first] + kept[1:]
```

The synopsis merges into the first kept prompt. That avoids two user messages in a row. The `summarize` argument is a stub here. In production it is a model call.

The proof is in the asserts. A `check_pairs` function lists every orphan `tool_use` or `tool_result`. The file also has a `naive_trim` that drops one message at a time. The asserts show that the naive version leaves an orphan at some budgets. They also show that `trim` and `compact` return a valid history at every budget in the range. The newest turn stays untouched, and an old decision survives in the synopsis.

## Use It

Claude Code runs this ladder for you. When the window fills, it clears older tool outputs first. Then it summarizes the conversation if needed. Your requests and key code snippets are kept. Detailed early instructions can be lost.

You can steer it. Add a "Compact Instructions" section to `CLAUDE.md`, or run `/compact` with a focus, such as `/compact focus on the API changes`. If one huge file refills the window after each summary, Claude Code stops auto-compacting after a few attempts and shows an error. It does not loop.

The Claude API also offers server-side compaction, where Claude writes the summary. Both the on-demand and the token-threshold kinds are in beta at the time of writing, so read the current docs before you build on them. Context editing clears old tool results by rule instead of summarizing them. Your own `summarize` function, as here, always works.

## Challenge

Make `compact` recursive. When the synopsis plus the kept turns still overflows, summarize again. Assert that a fact from the first summary is still in the final text.

## Sources

Claude Code docs, "How Claude Code works", section "When context fills up" (code.claude.com/docs/en/how-claude-code-works). Claude API docs, "Compaction overview" (platform.claude.com/docs/en/build-with-claude/compaction).

Next: [Persist, resume and checkpoints](../../04-persist-resume-and-checkpoints/docs/en.md)
