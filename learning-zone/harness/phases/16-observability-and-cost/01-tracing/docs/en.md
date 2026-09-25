# Tracing & spans for an agent

> **Motto** — A trace is the agent's flight recorder: nested spans for every call, timed and tagged.

*Part of Phase 16 — Observability & Cost.*

## The Problem

An agent run can go wrong in three ways: it runs slow, it costs too much, or it gives a
wrong answer. When that happens, you need to see *what happened* — which steps ran, how
long each took, and what each model or tool call did. Without **tracing** you're debugging
blind. A trace records a tree of **spans** (the loop, each model call, each tool call).
Each span carries a start/end time and attributes (tokens, tool name), so you can
reconstruct and diagnose any run.

## The Concept

<style>
.dgm-trc{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-trc-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-trc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-trc-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-trc-chain{display:flex;flex-direction:column;gap:2px}
.dgm-trc-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-trc-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-trc-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-trc{padding:20px 16px 18px}}
</style>
<div class="dgm-trc">
  <span class="dgm-trc-chip">One run, nested spans</span>
  <h4>The run span contains model-call spans and tool-call spans, which can nest further</h4>
  <p class="dgm-trc-sub">Bash calls nest under their tool span — the trace mirrors the actual call structure.</p>
  <div class="dgm-trc-chain">
    <div class="dgm-trc-node accent">Span: agent run</div>
    <div class="dgm-trc-arr">↓</div>
    <div class="dgm-trc-node alt">Span: model call (tokens, ms)</div>
  </div>
  <div class="dgm-trc-chain">
    <div class="dgm-trc-node alt">Span: tool call (name, ms)</div>
    <div class="dgm-trc-arr">↓</div>
    <div class="dgm-trc-node accent">Span: bash (exit, ms)</div>
  </div>
</div>


Spans nest — a tool span sits inside the run span, and each span carries its own timing and
attributes. It's the same model as distributed tracing, applied to an agent loop.

## Build It

`code/tracing.py` — a minimal nested-span tracer (a context manager):

```python
import time
from contextlib import contextmanager

class Tracer:
    def __init__(self):
        self.spans = []
        self._stack = []

    @contextmanager
    def span(self, name, **attrs):
        rec = {"name": name, "attrs": attrs, "children": [], "ms": None}
        (self._stack[-1]["children"] if self._stack else self.spans).append(rec)
        self._stack.append(rec)
        start = time.perf_counter()
        try:
            yield rec
        finally:
            rec["ms"] = round((time.perf_counter() - start) * 1000, 1)
            self._stack.pop()
```

```python
t = Tracer()
with t.span("run"):
    with t.span("model_call", tokens=120):
        pass
    with t.span("tool_call", tool="bash"):
        pass
print(t.spans[0]["name"], "->", [c["name"] for c in t.spans[0]["children"]])
```

The tracer builds a tree you can render or export. Each span knows its own duration and
attributes, so "why was this run slow?" becomes "which span dominated the time?".

## Use It

Claude Code, Codex, and the Agent SDK all emit traces and telemetry you can inspect. For a
custom harness, you wrap each model call and each tool call in a span yourself. Trajectory
evals (Phase 15) run over these traces. In production you export spans to a backend
(lesson 05), so every run stays diagnosable after the fact.

## Ship It

[`code/tracing.py`](../../01-tracing/code/tracing.py) — a nested-span tracer.

## Check Yourself

**Q1.** What is a span?

- A) the whole conversation
- B) a timed, attributed unit of work (a model/tool call) that nests into a trace tree
- C) a token
- D) a prompt

<details><summary>Answer</summary>B — the building block of a trace.</details>

**Q2.** Why trace an agent run?

- A) for fun
- B) to reconstruct and diagnose what happened (slow/expensive/wrong) after the fact
- C) to slow it down
- D) no reason

<details><summary>Answer</summary>B — observability enables diagnosis.</details>

**Challenge.** Add a `render()` that prints the span tree indented with durations, so a slow
run shows at a glance which span dominated.

## Related

- Builds on: Phase 2 — [The Agent Loop](../../../02-the-agent-loop/01-agent-loop/docs/en.md)
- Next: [Token & cost accounting](../../02-cost-accounting/docs/en.md)
- Used by: Phase 15 — trajectory evals
- [Roadmap](../../../../ROADMAP.md)
