# Compensation: undoing completed work

> **Motto** — You can't roll back what already committed. You can only run another
> action that puts the world right, and compensation is modelling that action next to
> the work it undoes.

*Part of Phase 04 — Service integration & error handling. Concept lesson — no code
required.*

## The Problem

Take a loan disbursal, three committed steps in: funds reserved at the treasury,
insurance policy issued, and then the e-agreement step discovers the applicant
withdrew. Transactions can't help. Each step committed long ago, across three
external systems that have no common rollback. But the business has an answer:
*release the reservation, cancel the policy*. Every mature operations team has these
"undo procedures." The question is whether they live in a wiki, executed by hand at
2 a.m. sometimes, or in the model, executed by the engine, in order, always.

## The Concept

Compensation is the saga pattern with a diagram. Each step that changes the world
gets a **compensation handler** — its undo action — attached like a boundary event.
If the process later throws a compensation event, the engine runs the handlers of
*completed* activities in reverse order:

<style>
.dgm-cmp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-cmp-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-cmp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-cmp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-cmp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-cmp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-cmp-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-cmp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-cmp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-cmp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-cmp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-cmp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-cmp{padding:20px 16px 18px}.dgm-cmp-row{flex-direction:column}}
.dgm-cmp-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-cmp-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-cmp-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-cmp-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-cmp-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-cmp-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-cmp-b.accent h6{color:#7a2c2e}
.dgm-cmp-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-cmp-b.blue h6{color:#0550ae}
.dgm-cmp-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-cmp-b.green h6{color:#1a614f}
.dgm-cmp-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-cmp-b.red h6{color:#82061e}
.dgm-cmp-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-cmp-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-cmp{padding:20px 16px 18px}.dgm-cmp-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-cmp">
  <span class="dgm-cmp-chip">Compensation undoes committed work</span>
  <h4>Compensation runs backwards through completed steps, not forwards</h4>
  <p class="dgm-cmp-sub">Each task can carry its own undo, triggered explicitly if the agreement is withdrawn.</p>
  <div class="dgm-cmp-row">
    <div class="dgm-cmp-n ">Reserve funds ⚙️</div>
    <span class="dgm-cmp-arr">→</span>
    <div class="dgm-cmp-n ">Issue policy ⚙️</div>
    <span class="dgm-cmp-arr">→</span>
    <div class="dgm-cmp-n accent">Sign agreement 👤</div>
    <span class="dgm-cmp-arr">→</span>
    <div class="dgm-cmp-n green">● end</div>
  </div>
  <div class="dgm-cmp-branches">
    <div class="dgm-cmp-b neutral">
      <h6>Compensate: reserve funds</h6>
      <p>↩ Release reservation ⚙️</p>
    </div>
    <div class="dgm-cmp-b neutral">
      <h6>Compensate: issue policy</h6>
      <p>↩ Cancel policy ⚙️</p>
    </div>
    <div class="dgm-cmp-b red">
      <h6>✖ Withdrawn after signing</h6>
      <p>Throw compensation → cancelled</p>
    </div>
  </div>
</div>


The rules that make it predictable:

1. **Only completed activities compensate.** If `issue policy` never ran, its handler
   never runs. The engine tracks what finished — the wiki procedure can't.
2. **Reverse order.** Undo happens newest-first, mirroring how the state was built
   (policy cancelled before the reservation that preceded it is released).
3. **Handlers are ordinary tasks** — usually service tasks calling your "cancel"
   APIs, occasionally user tasks ("manually reverse the ledger entry"). They can fail
   like any task, so lesson 05's retry/dead-letter pipeline applies to the *undo* too.
4. **Triggering is explicit.** A compensation throw event (often on the path out of an
   error boundary or a cancellation message) starts the unwind. Nothing compensates
   automatically just because something failed — you draw the decision.

When to reach for it — and when not:

| Situation | Answer |
| :-- | :-- |
| Multi-step external effects, later steps can abort the whole (booking, issuing, reserving) | **compensation** — this is the designed use |
| Failure within one transaction segment | plain rollback already covers it (Phase 2) |
| The "undo" is really a business process (refund approval, clawback with maker-checker) | model it as a normal subprocess — compensation handlers should be mechanical undos, not workflows |
| Only the last step ever fails | consider just reordering: do the risky step first |

Here's the honest cost: compensable processes roughly double the modelling and
testing surface, since every do has an undo, and undo paths need tests too. Use
compensation where the *sequence of external commitments* genuinely demands unwind,
not as decoration on every service task.

## Ship It

This lesson ships
[`outputs/compensation-patterns.md`](../outputs/compensation-patterns.md): the
pattern card with an XML skeleton, the four rules, and a checklist for deciding
whether a step needs a handler.

## Check Yourself

**Q1.** Compensation is thrown after steps A and B completed and C failed. Which
handlers run, in what order?

- A) A's, then B's
- B) B's, then A's — completed activities only, reverse order
- C) A's, B's and C's
- D) C's only

<details><summary>Answer</summary>B — C never completed, so it has nothing to undo.
The others unwind newest-first.</details>

**Q2.** A compensation handler calling the treasury's release API times out. What
happens?

- A) the engine gives up on compensation
- B) the original activity re-runs
- C) it's a technical failure like any other — retries, then dead letter (lesson 05)
- D) the instance completes anyway

<details><summary>Answer</summary>C — handlers are ordinary tasks on the ordinary
failure pipeline. Your undo paths need the same async/idempotency care as the do
paths.</details>

**Q3.** "Customer withdrew, so refund the processing fee — refunds need a
maker-checker approval." Model the refund as…

- A) a compensation handler on the fee-collection task
- B) a normal subprocess on the withdrawal path — it's a business process, not a mechanical undo
- C) a script task
- D) manual ops work outside the engine

<details><summary>Answer</summary>B — compensation handlers should be automatic
reversals. Anything with its own approvals, waits, and decisions is a process and
deserves to be modelled as one.</details>

**Challenge.** Take the capstone's disbursal sequence (reserve, issue policy,
disburse) and write its compensation table. For each step, note the undo API,
whether the undo is idempotent, and what happens if the undo itself dead-letters.
That table *is* the hard part of compensation — the XML takes twenty minutes.

## Related

- Phase README: [Service integration & error handling](../../README.md)
- The failure pipeline handlers run on: [Retries & incidents](../../05-retries-and-incidents/docs/en.md)
