# Add evals, observability & ship it

> **Motto** — Make it measurable, observable, and deployable — then it's a real product, not a demo.

*Part of Phase 19 — Capstone. Combines Phase 14 (reliability), 15 (evals), 16 (observability), 18 (deploy).*

## The Problem

The full-capability agent (project 03) is powerful but unproven and unobservable. The final
project wraps it with the production layers: **budgets + degraded mode** (P14) so it can't run
away, an **eval suite + gate** (P15) so changes are measured, **traces + cost** (P16) so runs
are diagnosable, and a **deploy checklist** (P18) so it ships safely. This is the curriculum,
complete: an agent you understand, trust, measure, and deploy.

## The Concept

<style>
.dgm-ca4{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ca4-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ca4 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ca4-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ca4-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-ca4-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-ca4-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-ca4-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-ca4-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-ca4-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-ca4-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-ca4-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-ca4{padding:20px 16px 18px}.dgm-ca4-row{flex-direction:column}}
</style>
<div class="dgm-ca4">
  <span class="dgm-ca4-chip">Capstone 4: the full agent, gated for production</span>
  <h4>Budgets, evals, traces, and a deploy checklist — the last four phases, in order</h4>
  <p class="dgm-ca4-sub">This is the same shape as Phase 18's deploy diagram, now applied to the capstone agent itself.</p>
  <div class="dgm-ca4-row">
    <div class="dgm-ca4-n neutral">Full agent (01–03)</div>
    <span class="dgm-ca4-arr">→</span>
    <div class="dgm-ca4-n accent">Budgets + degraded mode (P14)</div>
    <span class="dgm-ca4-arr">→</span>
    <div class="dgm-ca4-n blue">Eval gate (P15)</div>
    <span class="dgm-ca4-arr">→</span>
    <div class="dgm-ca4-n accent">Traces + cost (P16)</div>
    <span class="dgm-ca4-arr">→</span>
    <div class="dgm-ca4-n green">Deploy checklist (P18)</div>
  </div>
</div>


## Build It

`code/agent.py` (project 04) wraps the agent run with a budget, a tracer, and a cost meter,
and is gated by an eval suite:

```python
def run_observed(task, agent, budget, tracer, cost):
    with tracer.span("agent.run", task=task):
        if budget.exceeded():
            return {"status": "degraded", "reason": "budget"}     # P14
        out = agent(task)
        cost.record("claude-opus-5", 1000, 200, tag="capstone") # P16
        return {"status": "complete", "result": out,
                "trace": tracer.spans, "cost": cost.report()}
```

```python
report = run_observed("fix the bug", agent=lambda t: "fixed",
                      budget=Budget(), tracer=Tracer(), cost=CostMeter())
print(report["status"], report["cost"])     # complete, with cost attributed + a trace
# Then: eval_gate(run_evals(...)) before shipping (P15), deploy checklist (P18).
```

Every run is now bounded by budget, observable through trace and cost, and only ships if the
eval gate passes. This is the production wrapper around the agent you built in projects
01–03.

## Use It

This is the end state: a coding agent with the full harness — loop, tools, files, shell,
context, memory, permissions, subagents, MCP, retrieval, reliability, evals, observability,
and a deploy path. For a Claude Code / Codex user, it's the mental model of *everything the
platform does for you*, plus *everything you add*: `settings.json`, `CLAUDE.md`, hooks,
skills, MCP servers, CI evals. You finished the course. You can now build, operate, and
reason about a harness end to end.

## Ship It

[`code/agent.py`](../../04-evals-observability-ship/code/agent.py) — the production-wrapped
capstone agent (budget + trace + cost + eval gate).

## Check Yourself

**Q1.** What makes project 04 production-ready vs. project 03?

- A) nothing
- B) budgets/degraded mode, an eval gate, traces+cost, and a deploy checklist
- C) more tools
- D) a bigger model

<details><summary>Answer</summary>B — the reliability/eval/observability/deploy layers.</details>

**Q2.** The completed capstone is, in one phrase…

- A) a chatbot
- B) a coding agent with the full harness — built, measured, observable, deployable
- C) a prompt
- D) a single tool

<details><summary>Answer</summary>B — the whole curriculum, working.</details>

**Challenge.** Wire the real Phase 14 `Budget`, Phase 15 `run_evals`/`gate`, and Phase 16
`Tracer`/`CostMeter` into one runnable script, and add the Phase 18 `evals.yml` so it's gated
in CI. Then deploy it per the Phase 18 checklist.

## Related

- Combines: Phase 14, 15, 16, 18 (and every prior phase)
- Builds on: [Subagents/MCP/retrieval](../../03-subagents-mcp-retrieval/docs/en.md)
- 🎉 Course complete — see the [Roadmap](../../../../ROADMAP.md) for the full map.
- [Roadmap](../../../../ROADMAP.md)
