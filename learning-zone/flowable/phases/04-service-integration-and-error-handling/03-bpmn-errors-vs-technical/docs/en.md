# BPMN errors vs technical errors: two failure planes

> **Motto** — Ask one question of every failure: *would retrying change the answer?*
> No → it's a business outcome, model it. Yes → it's a technical fault, retry it.

*Part of Phase 04 — Service integration & error handling. Concept lesson — no code
required.*

## The Problem

The bureau call fails. But "fails" covers two completely different situations. One is
**"this PAN has no bureau file"** — a fact about the applicant, and calling again
won't conjure a file. The other is **"connection timed out"** — a fact about
infrastructure, and calling again in a minute may well succeed. Handle the first with
retries, and you loop pointlessly against a correct answer. Handle the second by
routing to a rejection path, and you decline loans because a router hiccuped. Most
workflow incidents in production trace back to these two planes being confused at
design time.

## The Concept

<style>
.dgm-bet{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-bet-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-bet h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-bet-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-bet-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-bet-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-bet-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-bet-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-bet-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-bet-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-bet-b.accent h6{color:#7a2c2e}
.dgm-bet-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-bet-b.blue h6{color:#0550ae}
.dgm-bet-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-bet-b.green h6{color:#1a614f}
.dgm-bet-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-bet-b.red h6{color:#82061e}
.dgm-bet-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-bet-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-bet{padding:20px 16px 18px}.dgm-bet-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-bet">
  <span class="dgm-bet-chip">Two failure families</span>
  <h4>Would retrying change the answer?</h4>
  <p class="dgm-bet-sub">An outcome is a BPMN error the diagram catches; a malfunction is a technical error the engine retries.</p>
  <div class="dgm-bet-q">A step fails</div>
  <div class="dgm-bet-branches">
    <div class="dgm-bet-b accent">
      <h6>No — it's an outcome</h6>
      <p>BPMN error: throw BpmnError('NO_BUREAU_RECORD') — caught by an error boundary or event subprocess, an explicit path on the diagram</p>
    </div>
    <div class="dgm-bet-b red">
      <h6>Yes — it's a malfunction</h6>
      <p>Technical error: any other exception — transaction rolls back; async retries then dead-letters, sync throws to the caller</p>
    </div>
  </div>
</div>


| | BPMN error | Technical error |
| :-- | :-- | :-- |
| What it means | a *business outcome* off the happy path | infrastructure/code malfunction |
| Raised by | `throw new BpmnError("CODE")`, error end event, HTTP task `failStatusCodes` | any other exception |
| Who sees it | **the diagram** — error boundary events, error event subprocesses | **operations** — retries, then the dead-letter table (Phase 2, lesson 04) |
| Transaction | token *moves* along the error flow (state advances, commits) | segment **rolls back**; no token movement |
| Retried? | never — it's an answer, not a fault | yes, if async (default 3×) |
| If uncaught | instance **fails** — an uncaught BpmnError is a modelling bug | dead-letter job / propagated exception |
| Examples | no bureau record, KYC mismatch, offer declined, limit exceeded | timeout, 502, `NullPointerException`, DB down |

Three design consequences:

1. **Error codes are part of your process's API.** `NO_BUREAU_RECORD`,
   `KYC_MISMATCH`, `LIMIT_EXCEEDED` — keep the set small, named, and documented.
   Boundary events subscribe by code. Catch-all boundaries (no code) are the
   `except Exception` of BPMN — legitimate as a last line, lazy as a first.
2. **Business people review business failures.** Because BPMN errors are on the
   diagram, "what happens when KYC fails?" is answered by pointing, not by reading
   Java. Being disciplined about the split keeps the diagram honest (Principle 2).
3. **Technical failures are invisible in the model — deliberately.** The diagram
   would drown if every timeout appeared on it. The engine's contract is: rollback,
   retry, dead-letter. Your job is monitoring that pipeline (lesson 05), not drawing
   it.

Here's the grey zone: *"bureau is down and ops wants a manual fallback after 3 failed
attempts."* That's a technical failure that **becomes** a business decision after it
persists. The pattern: let retries exhaust, then use the dead-letter handler (or
`handleTaskFailureAsBpmnError` on HTTP tasks) to convert the final failure into a
BPMN error the model routes. Escalation becomes visible in the diagram, while
transient blips stay out of it.

## Ship It

This lesson ships
[`outputs/failure-planes-cheatsheet.md`](../outputs/failure-planes-cheatsheet.md):
the decision table plus a review checklist for delegate code and models.

## Check Yourself

**Q1.** A delegate throws `BpmnError("LIMIT_EXCEEDED")` but no boundary event or event
subprocess catches it anywhere up the scope chain. The instance…

- A) retries the task
- B) fails — an uncaught BPMN error is a modelling bug, not a retryable fault
- C) completes normally
- D) dead-letters the job

<details><summary>Answer</summary>B — BPMN errors are never retried and don't
dead-letter. Uncaught means the model has a hole. Ship a catch-all boundary or fix
the model.</details>

**Q2.** The KYC service returns "documents don't match". The delegate should…

- A) throw `RuntimeException` so it retries
- B) throw `BpmnError("KYC_MISMATCH")` so the model routes to the re-submission path
- C) set a variable and return, hoping a gateway checks it
- D) log a warning

<details><summary>Answer</summary>B — a mismatch is an outcome, and retrying re-asks
a settled question. C *works* but hides the failure semantics — error events exist so
outcomes off the happy path are first-class.</details>

**Q3.** Which failure appears on the BPMN diagram?

- A) a 30-second bureau timeout
- B) `NullPointerException` in a delegate
- C) "applicant has no bureau record"
- D) database connection pool exhausted

<details><summary>Answer</summary>C — only business outcomes get drawn. A, B, D are
the job executor's problem and monitoring's problem.</details>

**Challenge.** Audit one real integration you own. List every way it fails, and tag
each one *outcome* or *malfunction*. Then check the code: how many outcomes are
currently thrown as generic exceptions, and therefore pointlessly retried? That list
is your error-code catalogue for the boundary events you'll build next lesson.

## Related

- Next: [Boundary events](../../04-boundary-events/docs/en.md) — build the catching side
- The retry pipeline: [Phase 2, lesson 04](../../../02-the-engine-state-and-transactions/04-job-executor/docs/en.md)
