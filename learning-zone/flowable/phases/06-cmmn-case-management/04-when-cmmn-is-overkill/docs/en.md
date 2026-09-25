# When CMMN is overkill (most of the time)

> **Motto** — Reach for CMMN only after BPMN has actually failed you in the modeler —
> not in the meeting where someone said "our process is too dynamic".

*Part of Phase 06 — CMMN: case management. Concept lesson — no code required. The
phase's honest closing.*

## The Problem

CMMN is elegant and standardised, and most organisations that adopted it
regret it. Camunda deprecated their implementation years ago for lack of use.
Flowable keeps a first-class one — it's genuinely good, and Flowable Work's
case UIs lean on it — but the industry pattern is clear. Teams choose CMMN in
the architecture phase for flexibility they never exercise, then pay its
costs for years: scarcer skills, weaker tooling ecosystems, harder testing,
and models reviewers can't read. This lesson is the checklist that keeps you
off that path, and the short list of cases where CMMN earns its keep.

## The Concept

Why "too dynamic for BPMN" is usually false — the three escape hatches you
already own:

<style>
.dgm-wco{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-wco-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-wco h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-wco-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-wco-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-wco-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-wco-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-wco-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-wco-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-wco-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-wco-b.accent h6{color:#7a2c2e}
.dgm-wco-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-wco-b.blue h6{color:#0550ae}
.dgm-wco-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-wco-b.green h6{color:#1a614f}
.dgm-wco-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-wco-b.red h6{color:#82061e}
.dgm-wco-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-wco-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-wco{padding:20px 16px 18px}.dgm-wco-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-wco">
  <span class="dgm-wco-chip">Reach for CMMN last</span>
  <h4>‘Our flow is too dynamic’ — have you tried these first?</h4>
  <p class="dgm-wco-sub">Most dynamism is really a boundary event, a loop, or a routing table in disguise.</p>
  <div class="dgm-wco-branches">
    <div class="dgm-wco-b blue">
      <h6>Event subprocesses (7.05)</h6>
      <p>React to X anytime, anywhere in scope</p>
    </div>
    <div class="dgm-wco-b green">
      <h6>Boundary events + loops (4.04, 1.02)</h6>
      <p>Exceptions &amp; rework paths</p>
    </div>
    <div class="dgm-wco-b accent">
      <h6>DMN routing (Phase 5)</h6>
      <p>Data-driven variation without drawing every variant</p>
    </div>
  </div>
  <div class="dgm-wco-q">Still not enough?</div>
  <div class="dgm-wco-branches" style="grid-template-columns:repeat(2,1fr)">
    <div class="dgm-wco-b red">
      <h6>Rarely</h6>
      <p>CMMN — lesson 06.02</p>
    </div>
    <div class="dgm-wco-b neutral">
      <h6>Usually</h6>
      <p>BPMN, simpler than feared</p>
    </div>
  </div>
</div>


Most "dynamic" requirements decompose into *interruptions* (event
subprocesses), *exceptions* (boundary events), *rework* (loops), and
*variants* (DMN-driven routing). What remains — genuine practitioner
authority over sequencing, lesson 01's litmus test — is rarer than the
meeting believes.

The real costs you accept with CMMN, spelled out:

| Cost | Why it bites |
| :-- | :-- |
| **Skills** | every engineer/BA knows some BPMN; CMMN fluency is rare — reviews, hiring, and handovers all pay |
| **Tooling & ecosystem** | modelers, linters, courses, StackOverflow depth — an order of magnitude thinner |
| **Testability** | a process has paths you can enumerate and assert; a case has *state spaces* — "any order, maybe never, maybe twice" multiplies test scenarios |
| **Legibility** | sentries encode logic invisibly (an AND across ON-parts, an IF-part in XML) — the diagram shows less of the behaviour than BPMN's does, the opposite of Principle 2's promise |
| **Ops intuition** | "where is case X stuck?" has fuzzier answers when nothing was ever *supposed* to happen next (Phase 9's oldest-instance signal needs rethinking per case model) |

CMMN genuinely earns it only when all three hold at once:

1. Practitioner authority over sequencing is *real and defended* — people
   like investigators, adjusters, and clinicians, whose judgment is the
   product.
2. The discretionary surface is *large*: a dozen-plus optional activities.
   Below that, one BPMN stage with event subprocesses covers it.
3. Guardrails still matter — sentries, milestones, required items. Without
   them, you wanted a task list, not an engine.

Fraud investigation (lesson 02) passes all three. Dispute handling passed by
*containing* its discretion in one stage (lesson 03). The capstone fails
condition 1 — and that's the normal case, which is the point.

## Ship It

This lesson ships
[`outputs/cmmn-adoption-checklist.md`](../outputs/cmmn-adoption-checklist.md) —
the escape hatches, the three-conditions test, and the containment strategy —
closing Phase 6 and, with it, the course's last engine.

## Check Yourself

**Q1.** "Our onboarding is too dynamic for BPMN — documents arrive in any
order." The first answer is…

- A) CMMN
- B) BPMN with event subprocesses / message catches per document — arrival order is an *event* problem (Phase 7), not a discretion problem
- C) a task list
- D) Temporal

<details><summary>Answer</summary>B — unordered *inputs* are not unordered
*work*. The litmus test asks who sequences the work, and onboarding's work
is prescribed.</details>

**Q2.** CMMN's testability cost comes from…

- A) slow engines
- B) state-space explosion — optional, repeatable, order-free items multiply the scenarios a test suite must cover versus a process's enumerable paths
- C) missing assertions
- D) XML

<details><summary>Answer</summary>B — discretion for the worker becomes
combinatorics for the tester. Budget for it, or constrain the model.</details>

**Q3.** The containment strategy for a mostly-prescribed flow with one
discretionary pocket is…

- A) model everything in CMMN for consistency
- B) BPMN end to end, with the pocket as a case (via case service task) or the case wrapping processes (lesson 03) — discretion quarantined where it's real
- C) two separate products
- D) gateway spaghetti

<details><summary>Answer</summary>B — lesson 03's seam exists precisely so
CMMN's costs are paid only on the stage that needs its powers.</details>

**Challenge.** Take lesson 02's fraud investigation and, as devil's advocate,
model it in plain BPMN using only the escape hatches. Write down exactly
where it breaks. Hint: "interview may repeat, statements may be skipped,
order is judgment" survives, and "escalation stage unlocked by evidence"
does too — what finally breaks is *completion semantics*. Knowing precisely
where BPMN fails is what earns you the right to use CMMN there.

## Related

- Phase README: [CMMN: case management](../../README.md)
- The escape hatches: [7.05](../../../07-events-timers-and-messaging/05-event-subprocesses/docs/en.md) · [4.04](../../../04-service-integration-and-error-handling/04-boundary-events/docs/en.md) · [Phase 5](../../../05-dmn-decisions/README.md)
