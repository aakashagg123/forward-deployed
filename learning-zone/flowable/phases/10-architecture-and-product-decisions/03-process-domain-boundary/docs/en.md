# Where the process ends and the domain begins: anti-corruption

> **Motto** — The engine owns *coordination state*; your domain owns *business
> truth* — the day a core service reads `ACT_RU_VARIABLE` for an answer, the
> boundary is gone and the engine has become your database.

*Part of Phase 10 — Architecture & product decisions. Concept lesson — no code
required. Concept reading:
[Principle 6](../../../../foundations/process-automation-principles.md).*

## The Problem

Engines are seductive state stores. Variables persist, history remembers, and the
API queries nicely. So the slide begins: the loan amount lives only as a process
variable, the mobile app renders account state from the task list, and reporting
joins `ACT_HI_VARINST` for revenue numbers.

Eighteen months later, the "workflow engine" is the system of record for a loan
book. Phase 9's retention decision has become a data-loss decision, and replacing
or even upgrading the engine means migrating your *business data*. Every BPM
veteran has seen this exact failure, and it has a boundary-shaped cure.

## The Concept

Two kinds of state, and the translation layer between them:

<style>
.dgm-pdb{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pdb-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-pdb h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pdb-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pdb-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dgm-pdb-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-pdb-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pdb-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-pdb-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pdb-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-pdb-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-pdb-col.neutral h6{color:#59636e}
.dgm-pdb-col.accent h6{color:#7a2c2e}
.dgm-pdb-col.blue h6{color:#0550ae}
.dgm-pdb-col.green h6{color:#1a614f}
.dgm-pdb-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-pdb-item:last-child{margin-bottom:0}
.dgm-pdb-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-pdb{padding:20px 16px 18px}.dgm-pdb-cols{grid-template-columns:1fr}}
.dgm-pdb-note{margin-top:10px;padding:9px 14px;background:#faeceb;border:1px dashed #e3b3ad;border-radius:10px;
  font-size:10.5px;color:#7a2c2e;line-height:1.4}
</style>
<div class="dgm-pdb">
  <span class="dgm-pdb-chip">The engine is not the domain</span>
  <h4>An anti-corruption layer keeps coordination state out of your domain model</h4>
  <p class="dgm-pdb-sub">IDs cross the boundary; payloads never do.</p>
  <div class="dgm-pdb-cols">
    <div class="dgm-pdb-col accent">
      <h6>Engine (coordination state)</h6>
      <div class="dgm-pdb-item">Where are the tokens</div>
      <div class="dgm-pdb-item">Who must act, by when</div>
      <div class="dgm-pdb-item">Which version, what path</div>
    </div>
    <div class="dgm-pdb-col neutral">
      <h6>Anti-corruption layer (delegates + facade)</h6>
      <div class="dgm-pdb-item">Translate: IDs across, payloads never</div>
    </div>
    <div class="dgm-pdb-col blue">
      <h6>Domain (business truth)</h6>
      <div class="dgm-pdb-item">Loan aggregate, Customer, ledger, documents — your services &amp; tables</div>
    </div>
  </div>
  <div class="dgm-pdb-note">Engine and domain never call each other directly — everything crosses through the anti-corruption layer, both ways.</div>
</div>


The four boundary rules:

1. **Variables carry references, not truth.** `loanId`, `applicationId`, and a
   `score` the flow routes on — yes. The loan's amount, rate schedule, or
   customer PII as the *only* copy — never. Phases 2.02 and 9.02 gave the
   tactical reasons (size, PII custody). This is the strategic one: variables
   are coordination scratchpad, and their retention clock must be allowed to run
   out.
2. **The translation lives in the delegates.** Phase 4's delegates and HTTP
   tasks are the anti-corruption layer. They call *domain APIs* and write back
   only the minimal routing facts. A delegate that reaches around its service to
   UPDATE domain tables directly has smuggled domain logic into the engine's
   transaction. That's convenient (Phase 2.05's atomicity) but corrosive,
   because now the domain's invariants are enforced from two places.
3. **Queries cross the boundary in one direction each.** "What must Asha do
   today?" goes to the engine (tasks, Phase 3). "What is loan L-401's balance?"
   goes to the domain. An app that renders *loan state* from *task state* has
   inverted the arrow — tasks say what's pending, never what's true.
4. **History is *process* audit, not business reporting.** "Who approved, when,
   under which version" goes to `ACT_HI_*` (Phases 8, 9). Revenue, portfolio,
   and NPA reporting go to domain events in your warehouse. Here's the test: if
   Phase 9's retention job deleting a row would lose business truth, that truth
   was in the wrong store.

Holding the line pays off. Engines become *replaceable* — the Phase 0 landscape
evaluation stays a real option forever. Retention stays a compliance dial rather
than a data-loss risk. Domain services stay testable without a running engine.
This also keeps model changes (Phase 8) cheap, because models orchestrate stable
APIs instead of touching schemas.

## Ship It

This lesson ships
[`outputs/boundary-review-guide.md`](../outputs/boundary-review-guide.md) — the
four rules as a review checklist, with the smell table for model and code review.

## Check Yourself

**Q1.** The mobile app shows loan status derived from the engine's open tasks.
The violation is…

- A) performance
- B) rule 3 inverted — task state says what's *pending*, not what's *true*; status belongs to the domain, which the process updates via delegates
- C) security
- D) none; that's what tasks are for

<details><summary>Answer</summary>B — the classic slide. The day the task list
renders customer-facing truth, the engine has become the system of
record.</details>

**Q2.** A delegate updates the `loans` table directly instead of calling the loan
service, "for atomicity". The cost is…

- A) none — Phase 2.05 blesses it
- B) domain invariants now enforced from two places; the loan service can no longer guarantee its own aggregate — atomicity was real, the boundary casualty too
- C) slower commits
- D) licensing

<details><summary>Answer</summary>B — embedded atomicity (2.05) is for *your
service's own* writes. Reaching into another service's tables through the engine
is the corruption the layer is named for.</details>

**Q3.** The test for "is this data in the wrong store" is…

- A) row count
- B) would Phase 9's retention deletion lose business truth? If yes, it was coordination-store data holding domain truth
- C) column type
- D) query speed

<details><summary>Answer</summary>B — retention is the boundary's enforcement
mechanism: coordination state must be *allowed* to expire.</details>

**Challenge.** Audit the capstone against the four rules. List every variable and
tag it reference, routing-fact, or truth. (`decision` and `rate` are the
interesting ones — routing facts the *domain must also record* via the disburse
delegate.) Then write the one-sentence answer to "why doesn't reporting query
ACT_HI_ directly?" for your data team.

## Related

- Next: [Build vs buy vs open source](../../04-build-vs-buy/docs/en.md)
- The tactical halves: [Phase 2, lesson 02](../../../02-the-engine-state-and-transactions/02-process-variables/docs/en.md) · [Phase 9, lesson 02](../../../09-operations-and-observability/02-history-levels/docs/en.md)
