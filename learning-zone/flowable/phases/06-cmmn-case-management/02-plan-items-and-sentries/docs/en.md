# Plan items, stages, milestones, sentries

> **Motto** — Four constructs carry all of CMMN: plan items are the possible work,
> stages group it, milestones mark achievement, and sentries are the *only* place
> sequencing pressure is allowed to live.

*Part of Phase 06 — CMMN: case management.*

## The Problem

Lesson 01 sold the paradigm. Now comes the vocabulary. CMMN's spec is
notoriously dense, but the working subset is four constructs. One deployable
case shows all of them: a fraud investigation where two evidence tasks can
run in any order, a milestone fires when both are done, and only *then* does
the escalation stage — legal referral, regulator report — become available.
Guardrails without a route.

## The Concept

<style>
.dgm-pis{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pis-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-pis h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pis-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pis-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-pis-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-pis-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pis-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-pis-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pis-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-pis-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-pis-col.neutral h6{color:#59636e}
.dgm-pis-col.accent h6{color:#7a2c2e}
.dgm-pis-col.blue h6{color:#0550ae}
.dgm-pis-col.green h6{color:#1a614f}
.dgm-pis-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-pis-item:last-child{margin-bottom:0}
.dgm-pis-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-pis{padding:20px 16px 18px}.dgm-pis-cols{grid-template-columns:1fr}}
.dgm-pis-chain{display:flex;flex-direction:column;gap:2px}
.dgm-pis-node{background:#faeceb;border:1.5px solid #e3b3ad;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#7a2c2e}
.dgm-pis-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-pis-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-pis{padding:20px 16px 18px}}
</style>
<div class="dgm-pis">
  <span class="dgm-pis-chip">Plan items &amp; sentries</span>
  <h4>Two plan items, a sentry, and a gated stage</h4>
  <p class="dgm-pis-sub">The stage doesn't exist as 'next' — it's enabled once both items complete, not skipped.</p>
  <div class="dgm-pis-cols">
    <div class="dgm-pis-col neutral">
      <h6>◻ Request statements</h6>
      <div class="dgm-pis-item">plan item — enabled at start</div>
    </div>
    <div class="dgm-pis-col neutral">
      <h6>◻ Interview customer</h6>
      <div class="dgm-pis-item">plan item — enabled at start</div>
    </div>
  </div>
  <div class="dgm-pis-chain">
    <div class="dgm-pis-node accent">⚑ Evidence complete — milestone (sentry: BOTH must complete)</div>
    <div class="dgm-pis-arr">↓</div>
    <div class="dgm-pis-node alt">Stage: escalation — unlocked (◻ refer to legal, ◻ file regulator report)</div>
  </div>
</div>


| Construct | Is | Lifecycle essence |
| :-- | :-- | :-- |
| **Plan item** | one unit of possible work (human task, process task, …) | available → enabled → active → completed; *the worker* moves it, not a token |
| **Stage** | a folder of plan items with its own entry/exit | opens like a scope; its items become available inside it |
| **Milestone** | a named achievement, no work of its own | *occurs* when its sentry fires — the case's progress vocabulary |
| **Sentry** | the guardrail: ON-parts (events: "X completed") + optional IF-part (condition on case data) | when satisfied → entry criterion enables the item / exit criterion terminates it |

Two semantics make CMMN genuinely different, not just different-shaped:

1. **Enablement, not invocation.** A satisfied entry sentry doesn't *start*
   work. It makes the item *available for the worker to start* (auto-start
   exists through `isBlocking`/manual-activation flags, but discretion is the
   default). Compare Phase 7's event subprocesses: the arming idea is the
   same, but there the event fires the work — here it only unlocks it.
2. **Completion is negotiated, not reached.** There is no end event. The
   case can complete when no required items are pending and nothing is
   active, or when the worker terminates it. "When is this case done?" is a
   modelling decision you make with required-rules. Forget it and you get
   immortal cases — the CMMN equivalent of Phase 1's dead-instance gateway
   bug.

## Use It

The full model —
[`outputs/fraud-investigation.cmmn`](../outputs/fraud-investigation.cmmn) — is
deployable to the stock Docker engine (the CMMN engine is in there; Phase 0's
map). The guardrail, in XML — a sentry with two ON-parts is an AND:

```xml
<sentry id="sentryEvidence">
  <planItemOnPart id="onStatements" sourceRef="piStatements">
    <standardEvent>complete</standardEvent>
  </planItemOnPart>
  <planItemOnPart id="onInterview" sourceRef="piInterview">
    <standardEvent>complete</standardEvent>
  </planItemOnPart>
</sentry>
```

Drive it over REST — same idioms as everywhere (`cmmn-repository/*`,
`cmmn-runtime/*`), and Phase 3's task API serves CMMN human tasks unchanged:

```bash
# deploy, then:
curl -su rest-admin:test -X POST .../cmmn-runtime/case-instances \
  -H 'Content-Type: application/json' -d '{"caseDefinitionKey": "fraudInvestigation"}'
# both evidence tasks are open AT ONCE (no order); complete them in either order;
# watch 'Refer to legal' and 'File regulator report' appear only after both.
```

That "appear only after" moment is the whole lesson. Nothing routed a token.
Completing the second evidence task satisfied a sentry, the milestone
occurred, the stage's entry criterion fired, and two new tasks became
available for a human to choose between.

## Ship It

This lesson ships
[`outputs/fraud-investigation.cmmn`](../outputs/fraud-investigation.cmmn) — the
four constructs in one deployable, REST-drivable case.

## Check Yourself

**Q1.** A satisfied entry sentry on a human-task plan item means…

- A) the task executes immediately
- B) the item becomes available/enabled — a person may now choose to start it (discretion is the default; auto-start is opt-in)
- C) the case completes
- D) a token moves

<details><summary>Answer</summary>B — enablement, not invocation. The worker
stays the scheduler.</details>

**Q2.** Two ON-parts in one sentry combine as…

- A) OR — either event fires it
- B) AND — all parts must be satisfied (want OR? give the item two entry criteria, each with its own sentry)
- C) XOR
- D) sequence

<details><summary>Answer</summary>B — within one sentry the parts combine as
AND. Multiple sentries on one item combine as OR. This is the most-quizzed
fact in CMMN, and misremembering it silently inverts your guardrail.</details>

**Q3.** A case with no required items and no exit criteria…

- A) completes when work runs out
- B) can linger forever — completion is a modelled decision; without required-rules or termination, you've built immortal cases
- C) errors at deploy
- D) completes after a timeout

<details><summary>Answer</summary>B — this is the CMMN counterpart of the
no-default-flow gateway: a correct legal model with an operational leak.
Decide completion explicitly.</details>

**Challenge.** Add an IF-part to `sentryEscalation` —
`${suspectedAmount > 1000000}` — so escalation unlocks only for large cases.
Then add a `repetitionRule` on the interview task, since real investigations
interview more than once. Deploy and verify both against the REST drill
above.

## Related

- Next: [Mixing BPMN and CMMN](../../03-mixing-bpmn-and-cmmn/docs/en.md)
- Task machinery reused: [Phase 3, lesson 01](../../../03-user-tasks-identity-and-forms/01-task-lifecycle/docs/en.md)
