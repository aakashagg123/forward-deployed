---
name: process-or-case-guide
description: The litmus test for BPMN process vs CMMN case, with traps on both sides
kind: decision-guide
phase: 06
lesson: 01
---

# Process or case? — the litmus test

**Who owns the order of work?**

- The organisation ("always X before Y") → **process (BPMN)**.
- The practitioner, within guardrails ("depends on the case") → **case (CMMN)**.

Apply per *stage*, not per system — most flows are processes containing at most
one discretionary pocket (model that pocket as a case, or the case calls
processes: lesson 03).

## Signals

| Toward process | Toward case |
| :-- | :-- |
| regulator/policy mandates sequence | expert judgment drives sequence |
| same path for 95% of instances | "every one is different" is actually true |
| SLA per step | SLA on the *outcome* only |
| steps mostly automated | steps mostly human investigation |
| deviations are exceptions to route | deviations are the normal mode |

## Traps

- **Hairball BPMN** — loops + inclusive gateways emulating discretion: you
  wanted a case (or one case-shaped stage).
- **Fake CMMN** — a case whose sentries chain every item into a fixed sequence:
  you rebuilt BPMN with worse tooling; go back.
- **"Dynamic" as an excuse** — teams claim discretion to avoid agreeing on a
  process; the litmus test forces the real conversation about who *should* own
  the order.
- **Discretion without guardrails** — a case with no required items, no
  sentries, no milestones is just a shared to-do list; the value is the
  guardrails.
