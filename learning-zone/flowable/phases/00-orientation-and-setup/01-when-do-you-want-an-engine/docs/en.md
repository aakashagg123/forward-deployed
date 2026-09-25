# What is a process engine, and when do you want one

> **Motto** — You want a process engine for one problem: *long-running, stateful,
> auditable coordination of humans, systems, and time.* Wait until you actually have
> that problem.

*Part of Phase 00 — Orientation & setup. Concept lesson — no code required. Concept
reading: [Principle 10](../../../../foundations/process-automation-principles.md).*

## The Problem

People usually ask "should we use a workflow engine?" backwards — after someone saw
a demo, not after diagnosing the pain. The pain that actually justifies one looks
like this: a business flow spans days or months. A `status` column tracks state,
and five services mutate it. Cron jobs enforce deadlines and drift over time. A SQL
archaeologist answers "where is case X stuck?" And an auditor asks which rules
version decided a case. If you have most of that list, an engine converts it into a
diagram, rows, timers, and history. If you don't, an engine converts a simple
system into a distributed one with extra ceremony.

## The Concept

A process engine makes three commitments in one runtime. Here is the whole course
in one diagram:

<style>
.dgm-wde{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-wde-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-wde h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-wde-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-wde-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-wde-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-wde-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-wde-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-wde-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-wde-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-wde-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-wde-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-wde{padding:20px 16px 18px}.dgm-wde-row{flex-direction:column}}
</style>
<div class="dgm-wde">
  <span class="dgm-wde-chip">The shape of this track</span>
  <h4>Three layers, one direction: model → state → services</h4>
  <p class="dgm-wde-sub">Each phase of this track adds a layer beneath the diagram you started with.</p>
  <div class="dgm-wde-row">
    <div class="dgm-wde-n neutral">An executable model — the diagram IS the code (Ph.1)</div>
    <span class="dgm-wde-arr">→</span>
    <div class="dgm-wde-n accent">A state machine with a database — waits are rows, not threads (Ph.2)</div>
    <span class="dgm-wde-arr">→</span>
    <div class="dgm-wde-n blue">Services around it — tasks, timers, history, retries, migration (Ph.3–9)</div>
  </div>
</div>


The diagnostic, as a table — count your yes-answers:

| Question | Engine says |
| :-- | :-- |
| Does the flow *wait* — for people, documents, deadlines — for days+? | wait states are its core trick |
| Do humans and systems interleave (review → API call → approval)? | task + service orchestration |
| Do deadlines/SLAs/expiries drive behaviour? | timers, versioned with the flow |
| Will audit/compliance ask "what happened and under which rules"? | history + definition pinning |
| Does the business change the flow more often than you deploy? | model + DMN redeploys |
| ≥ 4 yes | strong engine case |
| ≤ 2 yes | see the alternatives below |

Most flows *shouldn't* run on an engine. Here are the honest alternatives:

- **A `status` column + a queue** — for short, fully automated, rarely-changing
  flows. Three states and one retry policy don't need BPMN.
- **A saga/durable-execution runtime (Temporal-style)** — code-first orchestration
  for engineers. No diagram, no business-facing model (lesson 04 compares the two
  properly).
- **Event choreography** — services react to each other's events, with no central
  coordinator. You get maximal autonomy, but "where is case X?" has no single
  answer. That question is the exact reason an engine exists.

## Ship It

This lesson ships
[`outputs/engine-fit-checklist.md`](../outputs/engine-fit-checklist.md) — the
diagnostic plus the alternatives table. Bring it to the next "should we use a
workflow engine?" meeting.

## Check Yourself

**Q1.** Which flow is the *weakest* engine candidate?

- A) loan origination: humans, bureaus, offers expiring in 30 days
- B) image thumbnailing: 3 automated steps, seconds long, never changes
- C) vendor onboarding: documents, approvals, compliance audit trail
- D) claims handling: adjusters, deadlines, regulators

<details><summary>Answer</summary>B — no waits, no humans, no time, no audit
pressure. A queue and a worker do the job with less machinery.</details>

**Q2.** The strongest single signal *for* an engine is…

- A) many microservices
- B) flows that wait on humans/time for days while requiring a queryable, auditable position ("where is case X, under which rules?")
- C) high throughput
- D) a team that knows Java

<details><summary>Answer</summary>B — durable waiting plus accountability is the
combination nothing else provides as cheaply.</details>

**Q3.** Event choreography loses to orchestration precisely when…

- A) throughput is high
- B) someone must answer "where is this case and what happens next?" — choreography has no single place that knows
- C) services are polyglot
- D) events are JSON

<details><summary>Answer</summary>B — central state is orchestration's cost *and*
its product. Buy it when that question matters.</details>

**Challenge.** Run the diagnostic on three real flows in your organisation. For the
highest scorer, write a one-paragraph pitch *against* using an engine. If you can't
make a strong case for the alternative, you haven't finished the analysis.

## Related

- Next: [The Flowable platform map](../../02-platform-map/docs/en.md)
- The full comparison: [lesson 04](../../04-landscape/docs/en.md)
- Other tracks: [Prioritization & roadmaps](../../../../../technical-product-management/prioritization-and-roadmaps.md) · [Creativity: strategy & execution](../../../../../product-sense/creativity.md) — the build-vs-buy judgment behind adopting an engine at all.
