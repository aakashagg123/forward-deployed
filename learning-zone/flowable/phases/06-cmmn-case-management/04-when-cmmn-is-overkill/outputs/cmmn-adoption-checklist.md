---
name: cmmn-adoption-checklist
description: Gate CMMN adoption — escape hatches first, three-conditions test, containment strategy
kind: decision-guide
phase: 06
lesson: 04
---

# Before you adopt CMMN — the checklist

## 1. Exhaust the BPMN escape hatches (map each "dynamic" claim)

- [ ] Interruptions ("X can happen anytime") → event subprocesses (7.05)
- [ ] Exceptions ("when Y fails, humans take over") → error boundaries (4.04)
- [ ] Rework ("it can go back") → loops with exit conditions (1.02)
- [ ] Variants ("depends on segment/product") → DMN-driven routing (Phase 5)
- [ ] Unordered *inputs* ("documents arrive whenever") → message catches per
      input; the *work* may still be prescribed

Anything left after this table is candidate discretion. Usually: nothing is.

## 2. The three-conditions test (need ALL three)

- [ ] Practitioner authority over sequencing is real, defended, and desirable —
      their judgment is the product (investigators, adjusters, clinicians).
- [ ] The discretionary surface is large (≈ a dozen+ optional/repeatable
      activities; below that, one BPMN stage + hatches wins).
- [ ] Guardrails still matter (sentries/milestones/required items) — otherwise
      build a task list, not a case model.

## 3. If adopting: containment strategy

- [ ] Quarantine: CMMN only for the genuinely discretionary stage; prescribed
      neighbours stay BPMN, bridged per lesson 03 (process task / case service
      task).
- [ ] Completion semantics decided explicitly (required items, exit criteria) —
      no immortal cases.
- [ ] Test budget acknowledges state-space cost: scenario tests per sentry, not
      per path.
- [ ] Review capability exists: at least two people who can read sentries in XML.
- [ ] Ops signals redefined per case model ("stuck" ≠ oldest instance when
      nothing is *supposed* to happen next — Phase 9.04 adapted).

## The one-line policy

> BPMN by default; CMMN only where a named human's judgment over *ordering* is
> the feature — and then only for that stage.
