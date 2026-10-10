# Mixing BPMN and CMMN: process tasks inside cases

> **Motto** — The case decides *whether and when*; the process decides *how* — mixing
> lets each paradigm own exactly the half it's good at.

*Part of Phase 06 — CMMN: case management. This is the phase's **Use It** lesson.*

## The Problem

Lesson 01's litmus test rarely returns a pure answer. Take a card dispute.
Investigation is genuinely discretionary — contact, evidence review, all the
worker's call, in any order. But the *chargeback itself* is a scheme-mandated,
deadline-driven, prescribed sequence, as BPMN as anything in the capstone.
Force the whole thing into CMMN and you hand a regulated sequence to worker
discretion. Force it into BPMN and you're back to lesson 01's hairball. The
platform's answer (Phase 0's map) is to reference across engines, and let
each stage live in its own paradigm.

## The Concept

<style>
.dgm-mbc{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-danger-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mbc-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-danger-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-danger-solid) 28%, transparent)}
.dgm-mbc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-mbc-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-mbc-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-mbc-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-mbc-col.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-mbc-col.accent{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-mbc-col.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-mbc-col.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-mbc-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-mbc-col.neutral h6{color:var(--color-text-secondary)}
.dgm-mbc-col.accent h6{color:var(--color-text-danger)}
.dgm-mbc-col.blue h6{color:var(--color-text-info)}
.dgm-mbc-col.green h6{color:var(--color-text-success)}
.dgm-mbc-item{background:var(--color-surface);border:1px solid var(--color-border-info-surface);border-radius:8px;padding:6px 9px;font-size:10px;
  color:var(--color-text);line-height:1.35;margin-bottom:5px}
.dgm-mbc-item:last-child{margin-bottom:0}
.dgm-mbc-link{display:flex;justify-content:center;color:var(--color-text-tertiary);font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-mbc{padding:20px 16px 18px}.dgm-mbc-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-mbc">
  <span class="dgm-mbc-chip">A case that launches a process</span>
  <h4>Discretionary work up top, a prescribed process underneath</h4>
  <p class="dgm-mbc-sub">The process task is just one more discretionary item — until a sentry fires it.</p>
  <div class="dgm-mbc-cols">
    <div class="dgm-mbc-col accent">
      <h6>CMMN case: card dispute (discretion)</h6>
      <div class="dgm-mbc-item">◻ Contact customer</div>
      <div class="dgm-mbc-item">◻ Review evidence</div>
      <div class="dgm-mbc-item">▶ Chargeback process (process task)</div>
      <div class="dgm-mbc-item">▶ Goodwill refund process (process task)</div>
    </div>
    <div class="dgm-mbc-col blue">
      <h6>BPMN: chargebackProcess (prescription)</h6>
      <div class="dgm-mbc-item">File with scheme → Await response ⏰ → Post outcome</div>
    </div>
  </div>
  <div class="dgm-mbc-link">processRef, by key — review evidence sentry unlocks both process tasks</div>
</div>


The bridge constructs, both directions:

| Direction | Construct | Semantics |
| :-- | :-- | :-- |
| Case → process | CMMN **process task** (`processRefExpression`) | a plan item that, when started, launches a BPMN instance; blocking by default — the item completes when the process ends |
| Process → case | BPMN **case service task** | a process step that opens a CMMN case (e.g. capstone's fraud referral spawning an investigation) |

Design rules for the seam:

1. **Sentries gate the *launch*, BPMN owns the *inside*.** In the shipped
   model, neither chargeback nor refund is available until evidence review
   completes. But once launched, the chargeback's scheme deadlines (Phase 7
   timers) and retries (Phase 4) run under process discipline, untouchable by
   case discretion. The guardrail sits outside; the contract sits inside.
2. **Reference by key, version independently.** The case names
   `chargebackProcess`. Phase 8's whole apparatus applies to each artifact
   separately. When the scheme changes its rules, redeploy the process. When
   the ops team reorganises investigation, redeploy the case. Neither deploy
   touches the other.
3. **Variables cross explicitly.** Use in/out parameter mappings on the
   process task — not ambient sharing. The Phase 10.03 boundary discipline
   applies at this seam too: pass references and routing facts.
4. **Blocking vs non-blocking is a real decision.** Blocking is the default:
   the case item stays active until the process finishes, so the case *waits
   on* the how. Non-blocking is fire-and-continue: the case records that the
   process was launched and moves on. Chargeback stays blocking, because its
   outcome drives the case. A notification process stays non-blocking.

## Use It

The model — [`outputs/dispute-case.cmmn`](../outputs/dispute-case.cmmn) — with
the bridge in full:

```xml
<processTask id="ptChargeback" name="Chargeback (BPMN)"
    flowable:fallbackToDefaultTenant="true">
  <processRefExpression><![CDATA[chargebackProcess]]></processRefExpression>
</processTask>
```

Try this drill, a good afternoon exercise. Write a three-step
`chargebackProcess` in BPMN using Phase 1 skills — file, timer wait, post
outcome. Deploy both artifacts, start a dispute case, and watch the two
paradigms hand off. The chargeback plan item is *unavailable* until evidence
completes (sentry), then *available* after (the worker's choice — maybe this
dispute settles with a goodwill refund instead). Once started, its BPMN
innards march on rails. One case, one process instance, two clocks of
authority.

You've already almost met the reverse bridge. The capstone's challenge lesson
suggested a fraud referral — that's a BPMN **case service task** opening
lesson 02's `fraudInvestigation` from inside `loanOrigination`. Prescription
spawns discretion.

## Ship It

This lesson ships [`outputs/dispute-case.cmmn`](../outputs/dispute-case.cmmn) —
the mixing pattern as a deployable case, with both launch decisions
(chargeback/refund) gated by one evidence sentry.

## Check Yourself

**Q1.** In the dispute model, who decides *whether* a chargeback runs, and who
decides *how*?

- A) BPMN both
- B) the case worker decides whether/when (once the sentry enables it); the BPMN process owns how — steps, deadlines, retries
- C) CMMN both
- D) the customer

<details><summary>Answer</summary>B — the seam in one sentence: discretion
sits outside, the contract sits inside.</details>

**Q2.** A blocking process task completes…

- A) as soon as the process starts
- B) when the launched BPMN instance ends — the case waits on the outcome (non-blocking = fire-and-continue, for launches whose outcome the case doesn't consume)
- C) after a timeout
- D) when the worker closes it

<details><summary>Answer</summary>B — blocking is the default and the right
choice when case logic (sentries, milestones) depends on the process's
result.</details>

**Q3.** The scheme tightens chargeback deadlines. What redeploys?

- A) the case and the process
- B) only `chargebackProcess` — reference-by-key keeps the case untouched (Phase 8 applies per artifact)
- C) only the case
- D) both, atomically

<details><summary>Answer</summary>B — this is the same decoupling as BPMN→DMN
in Phase 5. The platform's cross-references exist exactly for independent
cadences.</details>

**Challenge.** Build the drill: the three-step `chargebackProcess` (with a
Phase 7 timer for the scheme's response window). Deploy both, then run one
dispute to a chargeback outcome and one to a goodwill refund. Then add the
reverse bridge — a case service task in the capstone's decline path opening a
retention case — and you've used every cross-engine reference on Phase 0's
map.

## Related

- Next: [When CMMN is overkill](../../04-when-cmmn-is-overkill/docs/en.md)
- The map of bridges: [Phase 0, lesson 02](../../../00-orientation-and-setup/02-platform-map/docs/en.md)
