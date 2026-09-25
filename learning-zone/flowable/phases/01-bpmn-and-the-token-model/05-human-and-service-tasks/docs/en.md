# User tasks vs service tasks: where humans and systems meet

> **Motto** — Every box in your process is a promise about *who* does the work and
> *how long the engine will wait*. Choose the task type by the promise, not the
> icon.

*Part of Phase 01 — BPMN & the token model. Concept lesson — no code required.
Concept reading: [Principle 6 — separate the flow from the work](../../../../foundations/process-automation-principles.md).*

## The Problem

Every real process is a braid of human judgment and system calls: an ops analyst
reviews the file, a bureau API returns a score, a rules engine decides, a customer
uploads a document. Model a human step as a service task, and the process
crashes looking for code that doesn't exist. Model an API call as a user task,
and it sits in somebody's inbox forever. Task-type choices are the requirements
document of your process, and they're the thing PMs and engineers most often get
wrong together.

## The Concept

The BPMN task family, sorted by *who acts* and *whether the engine waits*:

<style>
.dgm-hst{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-hst-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-hst h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-hst-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-hst-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-hst-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-hst-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-hst-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-hst-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-hst-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-hst-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-hst-col.neutral h6{color:#59636e}
.dgm-hst-col.accent h6{color:#7a2c2e}
.dgm-hst-col.blue h6{color:#0550ae}
.dgm-hst-col.green h6{color:#1a614f}
.dgm-hst-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-hst-item:last-child{margin-bottom:0}
.dgm-hst-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-hst{padding:20px 16px 18px}.dgm-hst-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-hst">
  <span class="dgm-hst-chip">Two families of BPMN task</span>
  <h4>Does the engine wait, or does it just act?</h4>
  <p class="dgm-hst-sub">Wait states persist and resume later; automatic tasks run to completion in one pass.</p>
  <div class="dgm-hst-cols">
    <div class="dgm-hst-col accent">
      <h6>Wait states — the engine sleeps</h6>
      <div class="dgm-hst-item">User task 👤 — a person completes it</div>
      <div class="dgm-hst-item">Receive task / message catch ✉️ — an external system calls back</div>
      <div class="dgm-hst-item">Timer ⏰ — the clock completes it</div>
    </div>
    <div class="dgm-hst-col blue">
      <h6>Automatic — engine acts and moves on</h6>
      <div class="dgm-hst-item">Service task ⚙️ — call code / expression</div>
      <div class="dgm-hst-item">HTTP task 🌐 — call a REST API</div>
      <div class="dgm-hst-item">Business rule task 📋 — evaluate a DMN table</div>
      <div class="dgm-hst-item">Script task 📜 — inline script (use sparingly)</div>
    </div>
  </div>
</div>


| Task type | Who acts | Wait state? | Typical fintech use |
| :-- | :-- | :-- | :-- |
| **User task** | a person (assignee / candidate group) | yes | manual credit review, maker-checker approval |
| **Receive / message** | an external system, later | yes | "wait for bureau callback", "wait for e-sign webhook" |
| **Service task** | your code, now | no | write-off posting, notification dispatch |
| **HTTP task** | a REST API, now (synchronously) | no | fetch CIBIL score inline |
| **Business rule task** | a DMN decision table | no | eligibility, pricing grid |
| **Script task** | inline script in the model | no | tiny glue only — real logic belongs in services |

Three decision rules cover 95% of modelling calls:

1. **"Does the flow stop until someone or something outside the engine acts?"**
   Yes → you need a wait state (user task, receive task, timer). No → use an
   automatic task.
2. **"Is the external call fast and reliable enough to hold a transaction open?"**
   A sub-second internal API can be a synchronous service task. A bureau that
   takes 30 seconds and fails at month-end must be an async call: fire a service
   task, then park at a message catch until the callback. Or mark the task async
   ([Phase 2, lesson 03](../../../02-the-engine-state-and-transactions/03-transactions-and-async/docs/en.md)).
3. **"Would the business want to change this logic without a release?"** Yes →
   it's not a script task, it's a DMN business rule task (Phase 5).

Watch for one anti-pattern in model reviews: **script tasks accumulating business
logic**. A script task is invisible to code review tooling, untestable in
isolation, and versioned only with the model. Two lines of glue are fine; an
eligibility rule never belongs there.

## Ship It

This lesson ships
[`outputs/task-type-guide.md`](../outputs/task-type-guide.md) — a one-page
decision guide. Paste it into your team's modelling conventions doc and use it in
model reviews.

## Check Yourself

**Q1.** The bureau API takes 5–40 seconds and is flaky at month-end. Best model?

- A) synchronous service task calling it inline
- B) user task assigned to ops, who query the bureau manually
- C) fire the request, then wait at a message catch for the callback (or async service task with retries)
- D) script task with a retry loop

<details><summary>Answer</summary>C — slow or unreliable externals must not hold the
engine's transaction open. Fire-and-wait (or async plus job retries) keeps the
instance durable across the flakiness.</details>

**Q2.** A maker-checker approval where any of five supervisors may act is best
modelled as…

- A) five parallel user tasks, one per supervisor
- B) one user task with a candidate group; whoever claims it, completes it
- C) a service task that emails all five
- D) a script task

<details><summary>Answer</summary>B — candidate groups are exactly this: one task,
many eligible claimants, first claim wins. Five parallel tasks would require all
five to act.</details>

**Q3.** Business asks to tweak the auto-approval threshold monthly. Where should that
logic live?

- A) a gateway condition in the BPMN model
- B) a script task
- C) a DMN decision table called from a business rule task
- D) hard-coded in the service layer

<details><summary>Answer</summary>C — logic the business wants to change on its own
cadence belongs in a decision table, deployable independently of process and
code.</details>

**Challenge.** Take one real process from your domain (loan disbursal, vendor
onboarding, refund approval). List every step, and for each write down: who acts,
does the engine wait, and what task type follows from rules 1–3. Where you
hesitate, that's where your requirements are actually unclear — that's the
point.

## Related

- Phase README: [BPMN & the token model](../../README.md)
- Next phase: [The engine: state & transactions](../../../02-the-engine-state-and-transactions/README.md)
