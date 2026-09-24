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

```mermaid
flowchart LR
  M["an executable model<br/>the diagram IS the code<br/>(Phase 1)"] --> E["a state machine<br/>with a database<br/>waits are rows, not threads<br/>(Phase 2)"]
  E --> S["services around it<br/>tasks, timers, history,<br/>retries, migration<br/>(Phases 3-9)"]
```

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
