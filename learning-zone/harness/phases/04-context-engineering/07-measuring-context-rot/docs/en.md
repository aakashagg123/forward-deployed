# Measuring context rot

> **Motto** — If you can't measure how a full window degrades answers, you're tuning blind.

*Part of Phase 04 — Context Engineering. Completes the phase.*

## The Problem

As the window fills, answer quality drops. The model misses a fact buried among thousands
of tokens, or anchors on stale content. This "context rot" is why budgeting, truncation,
and compaction matter. But which strategy actually helps? You can't tell without a metric.
This lesson builds a tiny eval that *measures* retrieval-from-context as the window grows.

## The Concept

A **needle-in-a-haystack** test hides a known fact (the needle) in filler (the haystack)
at varying depths and sizes. It then asks the model to recall the fact and scores accuracy.

<style>
.dgm-mcr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mcr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-mcr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-mcr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-mcr-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-mcr-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-mcr-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-mcr-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-mcr-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-mcr-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-mcr-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-mcr-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-mcr{padding:20px 16px 18px}.dgm-mcr-row{flex-direction:column}}
</style>
<div class="dgm-mcr">
  <span class="dgm-mcr-chip">Needle-in-a-haystack, scored on a grid</span>
  <h4>Vary depth and haystack size, then score whether the model still finds the needle</h4>
  <p class="dgm-mcr-sub">The result is an accuracy grid, not a single number — rot is depth-dependent.</p>
  <div class="dgm-mcr-row">
    <div class="dgm-mcr-n accent">Needle (known fact)</div>
    <span class="dgm-mcr-arr">→</span>
    <div class="dgm-mcr-n blue">Embed at depth d in haystack of size s</div>
    <span class="dgm-mcr-arr">→</span>
    <div class="dgm-mcr-n ">Ask model to recall</div>
    <span class="dgm-mcr-arr">→</span>
    <div class="dgm-mcr-n green">Score: found? → accuracy grid (s × d)</div>
  </div>
</div>


The output is a grid: accuracy by context size × needle depth. Rot shows up as cells
dropping off at large sizes or middle depths.

## Build It

`code/context_rot.py` — the harness, with a stub "model" so it runs offline (swap in a real
call for live numbers):

```python
def make_case(size, depth, needle="The launch code is 4242."):
    filler = "\n".join(f"filler line {i}" for i in range(size))
    lines = filler.splitlines()
    at = int(len(lines) * depth)
    lines.insert(at, needle)
    return "\n".join(lines), needle

def score(answer, needle_value="4242"):
    return 1 if needle_value in answer else 0

def run_grid(ask, sizes=(50, 500), depths=(0.1, 0.5, 0.9)):
    grid = {}
    for s in sizes:
        for d in depths:
            haystack, needle = make_case(s, d)
            answer = ask(haystack, "What is the launch code?")
            grid[(s, d)] = score(answer)
    return grid

def stub_ask(haystack, q):
    # Perfect recall for small contexts; "rots" past a threshold (illustrative).
    return "4242" if len(haystack) < 4000 else "I don't know"
```

```python
g = run_grid(stub_ask)
for (s, d), ok in g.items():
    print(f"size={s:4} depth={d}  {'FOUND' if ok else 'miss'}")
```

Swap `stub_ask` for a real call and you have a reproducible context-rot eval — the kind of
metric Phase 15 formalizes for the whole harness.

## Use It

This is the metric behind the advice you already follow in **Claude Code / Codex**.
Keep context lean, run `/clear` between tasks, and don't paste enormous files. When you
change how your harness assembles context, re-run a grid like this to prove the change
helped instead of guessing.

## Ship It

[`code/context_rot.py`](../../07-measuring-context-rot/code/context_rot.py) — a
needle-in-a-haystack context-rot eval.

## Check Yourself

**Q1.** What does a needle-in-a-haystack eval measure?

- A) latency
- B) whether the model can recall a known fact as context size/depth varies
- C) token cost
- D) tool accuracy

<details><summary>Answer</summary>B — recall vs. context size and position.</details>

**Q2.** Why measure context rot before changing your assembly strategy?

- A) it's required
- B) so you can prove a change helped instead of guessing
- C) to save tokens
- D) no reason

<details><summary>Answer</summary>B — measurement turns tuning into engineering.</details>

**Challenge.** Add multiple needles and report per-depth accuracy, then compare full-history
vs. compacted-history (lesson 04) on the same grid.

## Related

- Builds on: the whole phase
- Deepens in: Phase 15 — Evals & Testing the Harness
- Phase complete → next: Phase 5 — [Prompt & Instruction Architecture](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
