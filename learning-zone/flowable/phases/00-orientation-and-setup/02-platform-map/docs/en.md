# The Flowable platform map: BPMN, CMMN, DMN, event registry

> **Motto** — Flowable is four engines sharing one database and one API family:
> flows, cases, decisions, and events — each with its own model file, each
> deployable alone.

*Part of Phase 00 — Orientation & setup. Concept lesson — no code required.*

## The Problem

"Flowable" names a platform, not a single engine, and newcomers conflate the
parts. They model a decision as gateway spaghetti because they never met DMN.
They force ad-hoc casework into BPMN because CMMN was invisible to them. Or they
hand-roll a Kafka consumer that the event registry would have replaced. This
course spends whole phases undoing these mistakes. One map up front prevents most
of them, and explains what you inherited from the project's history: Flowable is
a 2016 fork of Activiti, built by that engine's original authors.

## The Concept

<style>
.dgm-pm{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-danger-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pm-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-danger-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-danger-solid) 28%, transparent)}
.dgm-pm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-pm-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-pm-cols{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.dgm-pm-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-pm-col.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-pm-col.accent{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-pm-col.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-pm-col.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-pm-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-pm-col.neutral h6{color:var(--color-text-secondary)}
.dgm-pm-col.accent h6{color:var(--color-text-danger)}
.dgm-pm-col.blue h6{color:var(--color-text-info)}
.dgm-pm-col.green h6{color:var(--color-text-success)}
.dgm-pm-item{background:var(--color-surface);border:1px solid var(--color-border-info-surface);border-radius:8px;padding:6px 9px;font-size:10px;
  color:var(--color-text);line-height:1.35;margin-bottom:5px}
.dgm-pm-item:last-child{margin-bottom:0}
.dgm-pm-link{display:flex;justify-content:center;color:var(--color-text-tertiary);font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-pm{padding:20px 16px 18px}.dgm-pm-cols{grid-template-columns:1fr}}
.dgm-pm-chain{display:flex;flex-direction:column;gap:2px}
.dgm-pm-node{background:var(--color-background-danger-surface);border:1.5px solid var(--color-border-danger-surface);border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:var(--color-text-danger)}
.dgm-pm-node.alt{background:var(--color-surface-tertiary);border-color:var(--color-border);color:var(--color-text)}
.dgm-pm-arr{display:flex;justify-content:center;color:var(--color-text-tertiary);padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-pm{padding:20px 16px 18px}}
</style>
<div class="dgm-pm">
  <span class="dgm-pm-chip">Flowable open-source platform</span>
  <h4>Four engines, one database, one API style</h4>
  <p class="dgm-pm-sub">BPMN, CMMN, DMN and the event registry are libraries over a shared schema.</p>
  <div class="dgm-pm-cols">
    <div class="dgm-pm-col accent">
      <h6>BPMN engine</h6>
      <div class="dgm-pm-item">flows: .bpmn20.xml · Phases 1–4, 7, 8</div>
    </div>
    <div class="dgm-pm-col blue">
      <h6>CMMN engine</h6>
      <div class="dgm-pm-item">cases: .cmmn · Phase 6</div>
    </div>
    <div class="dgm-pm-col green">
      <h6>DMN engine</h6>
      <div class="dgm-pm-item">decisions: .dmn · Phase 5</div>
    </div>
    <div class="dgm-pm-col neutral">
      <h6>Event registry</h6>
      <div class="dgm-pm-item">.event / .channel · Phase 7</div>
    </div>
  </div>
  <div class="dgm-pm-chain">
    <div class="dgm-pm-node alt">One relational database — ACT_RU_* / ACT_HI_* / ACT_DMN_* / ACT_CMMN_*</div>
    <div class="dgm-pm-arr">↓ all four engines write here ↓</div>
    <div class="dgm-pm-node accent">Shared service style — Repository / Runtime / Task / History · Java + REST</div>
  </div>
</div>


Here is what the map buys you in practice:

1. **One artifact type per question.** *What order do things happen?* → BPMN.
   *What work is available, human decides order?* → CMMN. *Which answer given
   these inputs?* → DMN. *What outside signal starts/continues work?* → event
   registry. A modelling smell (script-task rules, gateway policy constants,
   consumer glue services) usually means the question is in the wrong engine.
2. **Cross-references, not imports.** A BPMN decision task references a DMN key
   (Phase 5). A CMMN process task references a BPMN key (Phase 6). An event
   definition triggers either. Each artifact versions independently (Phase 8) —
   that independence is the governance story.
3. **One operational surface.** All four engines share the same database, the
   same history split, the same job executor family, and the same REST idioms.
   Phase 2 and Phase 9 apply to all four, which is why this course teaches the
   machinery once, through BPMN.
4. **Editions, briefly** (Phase 10 covers the decision in full). Everything
   above is the open-source core. *Flowable Work/Design* is the commercial
   layer — modelers, task UIs, admin consoles — on the same engines. Course
   rule: learn on the core, and evaluate the paid layer for its UIs, never for
   engine features.

## Ship It

This lesson ships [`outputs/platform-map.md`](../outputs/platform-map.md) — the
map, the artifact table, and the "which engine answers this question" router.

## Check Yourself

**Q1.** Eligibility rules keep growing inside gateway conditions. The platform-map
answer is…

- A) more gateways
- B) move them to a DMN decision table; the gateway routes on the result (Phase 5)
- C) a script task
- D) CMMN

<details><summary>Answer</summary>B — "which answer given inputs" is DMN's
question. Gateways route, and tables decide.</details>

**Q2.** A BPMN process uses a DMN table. When the table changes…

- A) the process redeploys too
- B) only the .dmn redeploys — cross-references by key keep lifecycles independent
- C) both must version-match
- D) the engine migrates instances

<details><summary>Answer</summary>B — reference-by-key is the platform's decoupling
mechanism. It's the reason Phase 5's governance works.</details>

**Q3.** The four engines share…

- A) nothing — separate products
- B) the database, the runtime/history split, the job machinery, and the API idioms — learn them once
- C) only the modeler
- D) a message bus

<details><summary>Answer</summary>B — one operational education covers the whole
platform, which is why this course teaches internals through BPMN alone.</details>

**Challenge.** Take the capstone and label every artifact with its engine (process,
decision table, event pair, and the hypothetical fraud-investigation case from
Phase 6). Then find one thing in *your* organisation's workflow landscape that's
currently in the wrong column.

## Related

- Next: [Run Flowable locally](../../03-run-locally/docs/en.md)
- Previous: [When do you want an engine](../../01-when-do-you-want-an-engine/docs/en.md)
