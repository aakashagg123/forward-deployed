# Event subprocesses & interrupting vs non-interrupting starts

> **Motto** — A boundary event guards one box; an event subprocess guards the whole
> scope — "while any of this is running, here's how we react to X."

*Part of Phase 07 — Events, timers & messaging. This is the phase's **Use It**
lesson.*

## The Problem

The customer can withdraw their application at *any* point — during document
collection, verification, review, or offer. Model that with boundary events, and
you pin the same withdrawal catch onto every activity: five copies that must stay
in sync through every model edit. Miss one, and withdrawal during that step becomes
silently impossible. The same shape recurs for "compliance freeze," "fraud flag
raised," and "send a status nudge weekly while open" — reactions that belong to the
*process as a whole*, not to any single box.

## The Concept

An event subprocess is a subprocess with `triggeredByEvent="true"`. It has no
incoming flows, it sits inside a scope, and its **start event** — message, timer,
signal, or error — arms when the scope becomes active:

<style>
.dgm-esp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-esp-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-esp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-esp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-esp-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dgm-esp-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-esp-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-esp-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-esp-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-esp-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-esp-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-esp-col.neutral h6{color:#59636e}
.dgm-esp-col.accent h6{color:#7a2c2e}
.dgm-esp-col.blue h6{color:#0550ae}
.dgm-esp-col.green h6{color:#1a614f}
.dgm-esp-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-esp-item:last-child{margin-bottom:0}
.dgm-esp-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-esp{padding:20px 16px 18px}.dgm-esp-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-esp">
  <span class="dgm-esp-chip">Two event subprocesses, one scope</span>
  <h4>Interrupting kills the main flow; non-interrupting runs beside it</h4>
  <p class="dgm-esp-sub">Both react to something arriving mid-process, without a boundary event on any one task.</p>
  <div class="dgm-esp-cols">
    <div class="dgm-esp-col neutral">
      <h6>Process scope — main flow</h6>
      <div class="dgm-esp-item">Collect docs 👤 → Verify docs 👤 → end</div>
    </div>
    <div class="dgm-esp-col red">
      <h6>⚡ Event subprocess: withdrawal (interrupting)</h6>
      <div class="dgm-esp-item">✉️ customerWithdrawal → Record withdrawal → end</div>
    </div>
    <div class="dgm-esp-col blue">
      <h6>⏰ Event subprocess: nudge (non-interrupting)</h6>
      <div class="dgm-esp-item">R/P7D → Send nudge → end</div>
    </div>
  </div>
</div>


The one attribute that changes everything is on the start event:

| `isInterrupting` | When it fires | Use for |
| :-- | :-- | :-- |
| `true` (default) | the scope's main flow is **terminated**; only the handler runs | withdrawal, fraud stop, hard cancellation |
| `false` | a **parallel** token runs the handler; main flow untouched; can fire repeatedly | nudges, escalations, audit pings |

Placement decides scope. At process level, it guards the whole instance. Inside an
embedded subprocess, it guards just that stage — a withdrawal handler that only
applies before disbursal, say. The error event subprocess variant is Phase 4's
scope-chain walking, drawn: errors uncaught by any boundary land in the enclosing
scope's error event subprocess before killing the instance.

Versus boundary events, the trade is *coverage vs precision*: one drawn element
covering the scope, or per-activity reactions where each step should respond
differently. The withdrawal case wants coverage. "This specific bureau call gets a
manual fallback" wanted the boundary instead (Phase 4).

## Use It

The full model is
[`outputs/application-with-events.bpmn20.xml`](../outputs/application-with-events.bpmn20.xml)
— a two-task main flow plus both handler flavours. The load-bearing lines:

```xml
<subProcess id="withdrawalHandler" triggeredByEvent="true">
  <startEvent id="withdrawalStart" isInterrupting="true">
    <messageEventDefinition messageRef="withdrawalMsg"/>
  </startEvent>
  ...
</subProcess>

<subProcess id="nudgeHandler" triggeredByEvent="true">
  <startEvent id="nudgeStart" isInterrupting="false">
    <timerEventDefinition><timeCycle>R/P7D</timeCycle></timerEventDefinition>
  </startEvent>
  ...
</subProcess>
```

Deploy it with Phase 1's client and run the drill:

1. Start an instance; `collectDocs` is waiting.
2. Deliver `customerWithdrawal` (lesson 02's REST correlation, business key =
   application). The open task **vanishes**, because the interrupting start killed
   the main flow. History shows `recordWithdrawal` ran, with `outcome = withdrawn`.
3. Start a second instance and leave it. Every 7 days — sooner if you shrink the
   cycle for the test — `sendNudge` executes while `collectDocs` stays open.
   Parallel tokens run; the main flow stays untouched.

## Ship It

This lesson ships
[`outputs/application-with-events.bpmn20.xml`](../outputs/application-with-events.bpmn20.xml)
— the withdrawal + nudge pattern the capstone embeds directly.

## Check Yourself

**Q1.** Withdrawal must be possible during any of five steps. Event subprocess beats
five boundary events because…

- A) boundary events can't catch messages
- B) one drawn element covers the scope and survives model edits; five copies drift and one always gets missed
- C) it's faster at runtime
- D) it isn't better

<details><summary>Answer</summary>B — scope-level reactions belong to the scope. Per
-activity boundaries are for per-activity responses.</details>

**Q2.** A non-interrupting timer event subprocess with `R/P7D` on a long-running
instance fires…

- A) once, then disarms
- B) every 7 days while the scope is active, each firing a parallel token; the main flow never notices
- C) only if the main flow is idle
- D) it can't use cycles

<details><summary>Answer</summary>B — non-interrupting + cycle is the recurring
-side-effect pattern: nudges, SLAs, sweep checks.</details>

**Q3.** Where does an error event subprocess sit in Phase 4's uncaught-error story?

- A) it replaces boundary events
- B) it's the scope-level rung of the catch chain: activity boundary first, then enclosing scopes' error event subprocesses, then the instance fails
- C) it only catches technical errors
- D) unrelated mechanism

<details><summary>Answer</summary>B — this is the same walking-outward search, with one
more place to land before "uncaught BpmnError = dead instance."</details>

**Challenge.** Add a third handler to the model: an interrupting **signal** event
subprocess for `complianceFreeze` (lesson 03's broadcast) that routes to a user task
"await compliance clearance" instead of ending the instance. Then answer this: after
clearance, how do you resume the main flow? That question reveals the difference
between *pausing* a process and *terminating* it.

## Related

- Phase README: [Events, timers & messaging](../../README.md)
- Boundary-level catching: [Phase 4, lesson 04](../../../04-service-integration-and-error-handling/04-boundary-events/docs/en.md)
