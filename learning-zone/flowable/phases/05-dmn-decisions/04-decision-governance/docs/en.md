# Who owns the rules? Decision governance for product teams

> **Motto** — A decision table without a named owner, a review ritual, and a test set
> is just an `if` statement with better fonts.

*Part of Phase 05 — DMN: decisions as tables. Concept lesson — no code required.
Concept reading: [Principle 7](../../../../foundations/process-automation-principles.md).*

## The Problem

The technology from lessons 01–03 delivers exactly one thing: policy that can change
without an engineering release. That is a *capability*, not an outcome. Handed out
without governance, it produces the failure modes every rules-engine veteran has
seen. The table nobody dares edit, because nobody remembers why row 17 exists. The
"quick change" that priced a segment negative for a weekend. The audit that finds
the table in production doesn't match the policy the committee approved. DMN moves
the risk from *deployment* to *authorship*, and authorship needs the same discipline
code got.

## The Concept

Four questions, answered per table and written down:

<style>
.dgm-dg{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-dg-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-dg h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-dg-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-dg-matrix{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-dg-cell{border-radius:11px;padding:11px 13px;position:relative;border:1.5px solid}
.dgm-dg-cell h6{margin:2px 0 4px;font-size:11px;font-weight:700}
.dgm-dg-cell p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-dg-cell.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-dg-cell.accent h6{color:#7a2c2e}
.dgm-dg-cell.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-dg-cell.blue h6{color:#0550ae}
.dgm-dg-cell.green{background:#dafbe1;border-color:#aceebb}
.dgm-dg-cell.green h6{color:#1a614f}
.dgm-dg-cell.red{background:#ffebe9;border-color:#ffcecb}
.dgm-dg-cell.red h6{color:#82061e}
.dgm-dg-cell.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-dg-cell.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-dg{padding:20px 16px 18px}.dgm-dg-matrix{grid-template-columns:1fr}}
</style>
<div class="dgm-dg">
  <span class="dgm-dg-chip">Governing a decision table</span>
  <h4>A decision table needs the same governance as a service</h4>
  <p class="dgm-dg-sub">Four things to nail down before the credit team can own it.</p>
  <div class="dgm-dg-matrix">
    <div class="dgm-dg-cell accent">
      <h6>1 · Owner</h6>
      <p>One accountable name (credit head, not 'the committee')</p>
    </div>
    <div class="dgm-dg-cell blue">
      <h6>2 · Change ritual</h6>
      <p>Who proposes, who approves, how it reaches the engine</p>
    </div>
    <div class="dgm-dg-cell green">
      <h6>3 · Validation</h6>
      <p>Golden cases + overlap/completeness checks before deploy</p>
    </div>
    <div class="dgm-dg-cell neutral">
      <h6>4 · Audit</h6>
      <p>Which version decided this case? (history + version pinning)</p>
    </div>
  </div>
</div>


**1. Ownership.** One name per table. The engineering smell test: if a UNIQUE
violation fires in production (lesson 02), does the alert route to a person who can
*fix the policy*? If it pages ops, ownership is unassigned.

**2. The change ritual.** The healthy pipeline looks like code review because it is
one: propose (edited table), diff (row-level — this is why tables beat prose policy
documents), approve (the owner plus a second pair of eyes), and deploy (new version
via the same CI that deploys models). The anti-pattern is edit-in-production
consoles. The capability to change policy in a browser is exactly why write access
to production tables should not exist.

**3. Validation.** Tables are data, so they're testable as data:

- **Golden cases** — a spreadsheet of input → expected output pairs the owner
  maintains. Every table version must pass before deploy. Your lesson-01 engine is a
  perfectly good runner for it.
- **Structural checks** — overlap detection for UNIQUE tables, completeness over
  representative inputs (the lesson-01/02 challenges), type checks on cells.
- **Impact replay** — before activating v8, run last month's real inputs through v7
  *and* v8 and diff the decisions. "This change flips 3.2% of applications from auto
  to manual" is the sentence the committee actually needs.

**4. Audit.** Two rules keep the regulator conversation short. History must record
*which table version* produced each decision (Flowable's DMN history does, if you
keep it — Phase 9's retention decision applies). In regulated flows, pin in-flight
instances to the version that started them rather than "latest" — the Phase 8
versioning discipline, applied to decisions.

One scope question precedes all four: **does this rule belong in a table at all?**
Here's the boundary from Phase 1's task-type guide, sharpened:

| Belongs in DMN | Belongs in code |
| :-- | :-- |
| thresholds, bands, grids the business recalibrates | algorithms (EMI math, scorecard computation) |
| eligibility and routing policy | validation of data shape/integrity |
| pricing components, fee schedules | anything needing loops, external calls, state |
| rules a regulator will ask to *see* | rules only engineers will ever touch |

## Ship It

This lesson ships
[`outputs/decision-governance-checklist.md`](../outputs/decision-governance-checklist.md):
the four questions as a per-table checklist, ready for your team's operating doc.

## Check Yourself

**Q1.** A UNIQUE violation fires in production. Who should the alert reach?

- A) ops, to retry the job
- B) the table's owner — it's a policy bug; retrying re-asks a broken question
- C) the customer
- D) nobody; it self-heals

<details><summary>Answer</summary>B — this is Phase 4's two-planes logic applied to
decisions. A table bug is not a transient fault, and the routing of its alert is the
practical test of whether ownership exists.</details>

**Q2.** The committee approves a band change. The *safest* path to production is…

- A) edit the table in the production console
- B) a new table version through diff → approval → CI deploy, after golden cases and an impact replay
- C) hotfix the gateway condition instead
- D) email the new table to engineering

<details><summary>Answer</summary>B — the whole pipeline exists to make policy
changes fast *and* reviewed. The console edit skips every safeguard the format makes
possible.</details>

**Q3.** "Recompute the EMI schedule for this rate" belongs…

- A) in a COLLECT table
- B) in code — it's an algorithm, not a policy; DMN holds the *rate*, code does the *math*
- C) in a script task
- D) in the gateway

<details><summary>Answer</summary>B — tables hold the numbers the business tunes, and
computation stays in tested code. Splitting exactly there keeps both sides
honest.</details>

**Challenge.** Pick one policy currently living in your codebase (a threshold, a
routing rule, a fee grid). Write its governance card: owner, change ritual, five
golden cases, and the impact-replay query you'd run before activating a change. If
you can't name the owner, you've learned why it's still in code.

## Related

- Phase README: [DMN: decisions as tables](../../README.md)
- Version pinning for in-flight work: Phase 8 (see [`ROADMAP.md`](../../../../ROADMAP.md))
- History retention for audit: Phase 9 (see [`ROADMAP.md`](../../../../ROADMAP.md))
- Other tracks: [Governance, quality & trust](../../../../../knowledge-graphs/governance-quality-and-trust.md) — governing decisions-as-data is the same trust problem as governing a knowledge graph.
