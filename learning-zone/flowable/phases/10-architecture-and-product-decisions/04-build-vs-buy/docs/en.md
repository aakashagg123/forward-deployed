# Build vs buy vs open source: the workflow TCO conversation

> **Motto** — You never choose whether to have a workflow platform — every lending
> product has one; you choose whether it's designed, and who you pay to keep it
> alive.

*Part of Phase 10 — Architecture & product decisions. Concept lesson — no code
required.*

## The Problem

The build-vs-buy meeting is usually fought with the wrong numbers: license fees
against "free," or sprint estimates against sales decks. The real comparison is
the total cost of a *capability* over five years. The biggest line items are the
ones this course spent nine phases on: the state machine (Phase 2), retries and
dead letters (4), timers (7), versioning of in-flight work (8), and operations
(9).

Teams that haven't named those items compare a visible license fee against an
invisible engineering mortgage. The DIY option wins meetings it should lose.

## The Concept

Three options, priced over the same five columns:

| Cost line | DIY (status + queues) | Open source (Flowable OSS) | Buy (Work / competitors) |
| :-- | :-- | :-- | :-- |
| **Core engine capability** (Phases 1–2, 4, 7, 8) | you build it — the full toy-engine syllabus, at production grade, forever | free, mature, 15-year lineage | included |
| **UIs** (modelers, inboxes, admin) | you build them | you build on the APIs (Phase 3 clients grow into this) | the actual product you're buying |
| **Operations** (Phase 9) | yours, plus the engine you wrote | yours — probe, retention, tuning, drills | reduced, not removed (their platform, your data) |
| **People** | senior eng, permanently — it's a product now | eng who've learned the engine (this course is the ramp) | fewer eng, plus vendor management |
| **Exit** | rewrite | migrate models to any BPMN engine (Phase 0.04's cell) | model portability minus proprietary UI/features |

The honest decision logic:

1. **DIY is a niche, not a default.** It wins only at Phase 0.01's low scores:
   short, automated, stable flows. Past that line, "build" means re-deriving
   Phases 2-9 under deadline pressure. The checklist below exists to make that
   mortgage visible in the meeting.
2. **Open source is a build decision in disguise, about the *edges*.** The
   engine is free and excellent. You are choosing to build UIs (Phase 3's
   clients grow into a real inbox), run the ops practice (Phase 9), and own
   upgrades. For a JVM product team with this course behind them, that's a
   known, bounded cost. It's often the right one in fintech, where the engine's
   DB rides your existing audit and residency story (Phase 0.04's axis).
3. **Buy when the bottleneck is the layer above the engine.** Many
   citizen-developer teams, heavy modeler usage, task UIs for hundreds of ops
   users, or a vendor SLA required by procurement — that's Work's actual
   product (10.01's third column). Buying an engine you'll only call over REST
   from your own UIs just pays for shelfware chrome.
4. **Count the option value of the standard.** BPMN and DMN artifacts outlive
   vendors: the capstone's XML deploys on Flowable today and Camunda tomorrow.
   DIY state machines and proprietary low-code flows have no such exit. Price
   that asymmetry, especially at contract renewal time.

## Ship It

This lesson ships
[`outputs/tco-worksheet.md`](../outputs/tco-worksheet.md) — the five cost lines
as a fill-in worksheet, plus the DIY-mortgage checklist for the meeting where
someone says "how hard can a workflow engine be?"

## Check Yourself

**Q1.** The most commonly *omitted* cost in DIY estimates is…

- A) hosting
- B) the engine capabilities themselves — durable waits, retries, timers, migration of in-flight work, the ops surface (Phases 2–9, at production grade, forever)
- C) licenses
- D) training

<details><summary>Answer</summary>B — the sprint estimate covers the happy path;
the mortgage is everything this course needed seven phases to even
*describe*.</details>

**Q2.** "Open source is free" is wrong because you're actually choosing…

- A) hidden license fees
- B) to build the edges — UIs, ops practice, upgrade ownership — around a free core; a bounded, known build if the team has the skills
- C) worse engines
- D) nothing; it is free

<details><summary>Answer</summary>B — OSS shifts spend from license to
engineering, at the edges rather than the core. Whether that's the right trade
is a team-shape question.</details>

**Q3.** The strongest signal to *buy* is…

- A) the engine lacks features
- B) the constraint is above the engine: modeler-heavy business users, large ops-user task UIs, procurement-mandated vendor SLA
- C) budget surplus
- D) microservices

<details><summary>Answer</summary>B — engines are commoditised by the standard;
the commercial products differentiate on the human layer. Buy where your
bottleneck actually is.</details>

**Challenge.** Fill the worksheet for the capstone platform three ways: DIY, OSS,
and buy, with your organisation's real day-rates and team shape. Then write the
sentence that would change your answer: "we would switch from OSS to buy the day
___." The trigger, not the snapshot, is what the annual review needs.

## Related

- Next: [The competitive matrix](../../05-competitive-landscape/docs/en.md)
- The capability being priced: [Phase 0, lesson 01](../../../00-orientation-and-setup/01-when-do-you-want-an-engine/docs/en.md)
