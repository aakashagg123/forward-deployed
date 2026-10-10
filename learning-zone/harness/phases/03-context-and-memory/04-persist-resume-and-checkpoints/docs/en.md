# Persist, resume and checkpoints

> **Motto** — A session you can save is a session you can resume. Resume from the last checkpoint, never from zero.

*Part of Phase 03 — Context and memory.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

You close the terminal. The process crashes. You come back tomorrow. Unless the harness saved the work, it is gone.

There are two kinds of loss. The first is the conversation: the message history and the notes the agent kept. The second is progress inside a long task. If a run dies in phase 3 of 5, a harness without checkpoints redoes phases 1 and 2. That wastes time and can repeat side effects, such as a second commit or a second email.

Both fixes use the same tool: write state to disk, and read it back on start.

## The Concept

<style>
.dgm-pr{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pr-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-pr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-pr-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-pr-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-pr-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-pr-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-pr-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-pr-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-pr-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-pr-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-pr-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-pr{padding:20px 16px 18px}.dgm-pr-row{flex-direction:column}}
.dgm-pr-lane{font-size:9.5px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary);text-align:center;margin:0 0 6px}
</style>
<div class="dgm-pr">
  <span class="dgm-pr-chip">Serialize to disk, load to resume</span>
  <h4>Session round trip, plus a checkpoint branch</h4>
  <p class="dgm-pr-sub">Resume skips the phases that already finished. Writes are atomic: temp file, then rename.</p>
  <p class="dgm-pr-lane">Session</p>
  <div class="dgm-pr-row">
    <div class="dgm-pr-n accent">Session: history + scratchpad</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n blue">Serialize → session.json</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n neutral">Disk</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n ">Load → restore</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n green">Continue the agent loop</div>
  </div>
  <p class="dgm-pr-lane" style="margin-top:14px">Checkpoint</p>
  <div class="dgm-pr-row">
    <div class="dgm-pr-n accent">Phase done</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n blue">Record what finished and changed</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n ">On resume</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n green">Skip finished phases</div>
  </div>
</div>


Three pieces of state matter.

- **History.** The messages, including every tool pair. The round trip must keep pairs whole (see [Trim and compact](../../03-trim-and-compact/docs/en.md)).
- **Scratchpad.** A small key/value store of working notes: the file being edited, a value computed, a decision made. It lives outside the history, so it survives trimming. Inject its summary when the agent needs a refresher.
- **Checkpoints.** After each phase of a task, record what finished and what changed. On resume, skip finished phases.

One rule protects all three: write atomically. Write a temp file, then rename it over the real file. A crash then leaves the old good file, never half a file.

## Build It

`code/session_store.py` has four parts: an atomic writer, a `Scratchpad`, a `SessionStore`, and a checkpointed task runner.

```python
def atomic_write(path, data):
    """Write to a temp file, then rename. A process crash never leaves a half-written file. For power-loss safety, also call `os.fsync` before the rename."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)                        # one atomic step
    except BaseException:
        os.unlink(tmp)
        raise
```

```python
def run_task(path, phases):
    """Run phases in order. Skip any phase the checkpoint file records as done."""
    state = read_json(path, {"done": []})
    for name, work in phases:
        if name in [d["phase"] for d in state["done"]]:
            continue
        result = work()                              # may raise: the crash case
        state["done"].append({"phase": name, "changes": result})
        atomic_write(path, state)                    # checkpoint after every phase
    return state
```

The asserts at the end test four cases. Resume restores history with its tool pair and the scratchpad. A save that dies halfway leaves the last good file, and no temp file behind. A missing file loads as an empty session. A task that crashes in phase 3 resumes in phase 3: the calls list shows `scaffold` and `implement` ran once, and `test` ran twice, once failing and once passing.

Checkpoints only help if phases are safe to skip. A phase that ran but did not record its checkpoint will run again. Make such phases idempotent, as [Budgets, idempotency and degraded mode](../../../09-reliability-evals-and-ops/02-budgets-idempotency-degraded-mode/docs/en.md) explains.

## Use It

Claude Code saves each conversation locally. Every message, tool use and result goes to a plaintext JSONL file under `~/.claude/projects/`. `claude --continue` or `claude --resume` reopens a session under the same ID and appends to it. `--fork-session` or `/branch` copies the history into a new session and leaves the original unchanged.

Claude Code also keeps file checkpoints. Before it edits a file, it snapshots the contents. Press `Esc` twice to rewind. Checkpoints are separate from git. They cover file edits only, not databases, APIs or deployments. Sessions are independent: a new session starts with a fresh window. Facts that must cross sessions belong in `CLAUDE.md` or in memory (next lesson).

## Challenge

Add a `--resume` flag to the REPL from [First call and REPL](../../../01-foundations-and-the-loop/01-first-call-and-repl/docs/en.md). Save after every turn. On start with the flag, load the last session. Assert that the resumed history ends with the same message that was saved.

## Sources

Claude Code docs, "How Claude Code works", sections "Work with sessions" and "Undo changes with checkpoints" (code.claude.com/docs/en/how-claude-code-works).

Next: [Long-term memory](../../05-long-term-memory/docs/en.md)
