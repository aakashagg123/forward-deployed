# Flowable open source vs Flowable Work vs Camunda 8 vs Temporal

> **Motto** — After eleven phases you can evaluate engines by their internals, not
> their websites: ask each candidate the course's questions and the matrix fills
> itself.

*Part of Phase 10 — Architecture & product decisions. Concept lesson — no code
required. This is Phase 0, lesson 04's rematch, with everything you've built since.*

## The Problem

Phase 0's landscape gave you two axes for a cold start. Now you know what a wait
state costs, what migration risk feels like, and what the ops surface demands.
The final comparison can be what real selections need: the same course-derived
question set put to all four serious candidates, with answers that survive a
proof-of-concept.

This is also the lesson to reread the day a renewal, a Camunda 8 pitch, or a
"should we move to Temporal" thread lands.

## The Concept

The course's seven questions, asked of all four:

| Course question | Flowable OSS | Flowable Work | Camunda 8 | Temporal |
| :-- | :-- | :-- | :-- | :-- |
| **Where do waits live?** (Ph. 2) | rows in your RDBMS | same | Zeebe's replicated log | event history in its cluster; workers replay code |
| **Human tasks & identity?** (Ph. 3) | native tasks, pools, forms; BYO UI | native + shipped task UIs | native + Tasklist app | DIY — activities + your own task store/UI |
| **Failure planes?** (Ph. 4) | BpmnError vs retries/dead letters, as taught | same | same model on Zeebe incidents | code-level: retries/compensation in workflow code; no business-error-on-diagram |
| **Decisions?** (Ph. 5) | DMN engine, independent deploys | + decision modeler UI | DMN supported | none — rules are code or an external service |
| **Time & correlation?** (Ph. 7) | timers/messages/event registry | same + UI | timers/messages native | first-class timers & signals in code — genuinely excellent |
| **In-flight versioning?** (Ph. 8) | pin + migrate, as taught | same + tooling | version pinning; migration tooling | workers must keep old code paths alive (patching/worker versioning) — the hardest part of Temporal at scale |
| **Ops surface?** (Ph. 9) | your probe on your DB | + admin UIs | Operate app; unified Orchestration Cluster with internal history (since 8.8, no separate exporter pipeline) | its own cluster metrics; history is replay fuel, not SQL |

Reading the columns like an owner:

1. **Flowable OSS vs Work is *only* the edges question** (10.04). Both run the
   same engines and give the same answers to every internals row. Work adds
   modelers, task and admin UIs, CMMN-heavy case UIs, and a vendor SLA. Decide
   by counting UI users, not by engine features.
2. **Camunda 8 is the same *language*, different *physics*.** BPMN semantics
   you already know, but state moves from your RDBMS to Zeebe. Phase 2's and
   Phase 9's chapters get rewritten — the Orchestration Cluster's built-in
   history instead of ACT_HI_ SQL, platform ops instead of DB ops. Choose it
   for genuine throughput ceilings or its SaaS, not as "newer Camunda 7."
3. **Temporal's column is consistent, and consistently code.** It has superb
   durable execution and real timers and signals, but humans, decisions, and
   diagrams are all DIY. Its versioning row deserves special respect: "old code
   paths in workers forever" is Phase 8's problem *without* the migration
   tooling.
4. **The PoC that settles it** (two weeks, either finalist): the capstone.
   Parallel checks, an error-boundary fallback, a DMN decision, a timed offer,
   one migration mid-flight, and the Phase 9 probe pointed at it. Any candidate
   that makes those two weeks miserable has answered the evaluation.

## Ship It

This lesson ships
[`outputs/competitive-matrix.md`](../outputs/competitive-matrix.md) — the
seven-question matrix plus the PoC script, closing Phase 10 and the course's
concept track.

## Check Yourself

**Q1.** Flowable Work's differentiation over OSS is…

- A) a faster engine
- B) the human layer — modelers, task/admin UIs, SLA — on identical engines; it's 10.04's buy-the-edges decision
- C) exclusive DMN
- D) cloud only

<details><summary>Answer</summary>B — every internals row matches OSS. Price the
UIs against building on Phase 3's clients.</details>

**Q2.** Migrating from Camunda 7-class engines to Camunda 8 is nontrivial mostly
because…

- A) BPMN files don't open
- B) the state substrate changes — RDBMS rows to Zeebe log — so embedding, transactions (Ph. 2), and the SQL-flavoured ops story (Ph. 9) all change with it
- C) licensing
- D) DMN was removed

<details><summary>Answer</summary>B — same modelling language, different physics.
The diagram ports; your Phases 2 and 9 practices don't, unchanged.</details>

**Q3.** Temporal's hardest scale problem, in this course's vocabulary, is…

- A) throughput
- B) Phase 8 without the tooling — in-flight versioning means workers carrying old code paths (patch/version discipline) instead of pin-and-migrate
- C) timers
- D) retries

<details><summary>Answer</summary>B — durable execution moves versioning from
engine feature to team discipline. Ask any large Temporal shop about workflow
patching.</details>

**Challenge.** Run the PoC script mentally against a *fifth* candidate — any
low-code or iPaaS workflow tool procurement suggests. Note which of the seven
questions it can't answer at all. That gap analysis, written up in an email, has
ended more bad evaluations than any matrix.

## Related

- Phase README: [Architecture & product decisions](../../README.md)
- The cold-start version: [Phase 0, lesson 04](../../../00-orientation-and-setup/04-landscape/docs/en.md)
