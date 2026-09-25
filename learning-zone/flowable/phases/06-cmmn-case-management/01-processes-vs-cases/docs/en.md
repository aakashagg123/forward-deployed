# Processes vs cases: prescribed flow vs available work

> **Motto** — BPMN says "do this, then this"; CMMN says "while the case is open,
> these things *may* happen" — one models a route, the other a workspace.

*Part of Phase 06 — CMMN: case management. Concept lesson — no code required.
Concept reading:
[Principle 8](../../../../foundations/process-automation-principles.md).*

## The Problem

Try to model a fraud investigation in BPMN and watch it fight you. The
investigator might request statements, interview the customer, call the bank,
or escalate — in any order, some steps never happen, others repeat, and
judgment drives the choice. Your diagram becomes a hairball of loops and
inclusive gateways. It tries to *prescribe* work that is inherently
*discretionary*. That is not a modelling skill gap. It is a paradigm
mismatch. BPMN assumes a knowable happy path, and that assumption does not
hold for knowledge work. CMMN exists for exactly this kind of work.

## The Concept

The inversion, side by side:

<style>
.dgm-pvc{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pvc-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-pvc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pvc-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pvc-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-pvc-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-pvc-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pvc-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-pvc-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pvc-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-pvc-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-pvc-col.neutral h6{color:#59636e}
.dgm-pvc-col.accent h6{color:#7a2c2e}
.dgm-pvc-col.blue h6{color:#0550ae}
.dgm-pvc-col.green h6{color:#1a614f}
.dgm-pvc-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-pvc-item:last-child{margin-bottom:0}
.dgm-pvc-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-pvc{padding:20px 16px 18px}.dgm-pvc-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-pvc">
  <span class="dgm-pvc-chip">Prescribed flow vs. available work</span>
  <h4>BPMN says what happens next; CMMN says what's possible now</h4>
  <p class="dgm-pvc-sub">A case is a folder of discretionary work, not a fixed path.</p>
  <div class="dgm-pvc-cols">
    <div class="dgm-pvc-col accent">
      <h6>BPMN — prescribed flow</h6>
      <div class="dgm-pvc-item">Collect → Verify → Decide (fixed order)</div>
    </div>
    <div class="dgm-pvc-col blue">
      <h6>CMMN — available work</h6>
      <div class="dgm-pvc-item">Case: fraud investigation (a folder of possible work)</div>
      <div class="dgm-pvc-item">◇ Request statements</div>
      <div class="dgm-pvc-item">◇ Interview customer</div>
      <div class="dgm-pvc-item">◇ Escalate to legal (only after evidence milestone)</div>
    </div>
  </div>
</div>


| | BPMN process | CMMN case |
| :-- | :-- | :-- |
| Core metaphor | a route: tokens move along flows | a workspace: plan items become available/active/completed |
| Order | the model decides | the *case worker* decides, within guardrails |
| "Next step" | whatever the token faces | whatever is enabled — possibly several, possibly none |
| Guardrails | sequence flows, gateways | **sentries**: "X becomes available when Y completes / when data says so" |
| Completion | tokens reach end events | required items done, nothing active — or worker closes it |
| Home turf | origination, payments, onboarding — the whole course so far | investigations, disputes, complex claims, advisory work |

The litmus test is one question: **who owns the order?** If the
*organisation* owns it ("KYC before decision, always" — every capstone
step), it's a process. If the *practitioner* owns it ("interview first or
statements first? it depends on the case"), it's a case. Most real systems
are processes with a few discretionary pockets. That is why lesson 03's
mixing pattern — cases calling processes, and processes calling cases —
matters more than pure CMMN. It is also why lesson 04 warns you how rarely
*pure* CMMN is the right answer.

Here is a mental bridge from what you've already built. A CMMN case behaves
like a scope full of Phase 7 event subprocesses — units of work that arm
when their condition holds — but the *human* is the event source. The engine
machinery underneath is the same (Phase 2's rows, Phase 3's tasks). Only the
authority over sequencing changes.

## Ship It

This lesson ships
[`outputs/process-or-case-guide.md`](../outputs/process-or-case-guide.md) — the
litmus test and the traps on both sides.

## Check Yourself

**Q1.** The question that sorts process from case is…

- A) how many steps there are
- B) who owns the order — the organisation (process) or the practitioner within guardrails (case)
- C) whether humans are involved
- D) data volume

<details><summary>Answer</summary>B — humans appear in both (Phase 3 is all
process-side humans). Discretion over *sequencing* is the divider.</details>

**Q2.** In CMMN, sequencing pressure ("escalation only after evidence complete")
is expressed by…

- A) sequence flows
- B) sentries gating a plan item's availability on other items' completion or case data
- C) gateway conditions
- D) it can't be expressed

<details><summary>Answer</summary>B — sentries are guardrails on *availability*,
not a route. The worker still chooses among whatever is enabled.</details>

**Q3.** Loan origination (the capstone) is a process, not a case, because…

- A) it has service tasks
- B) the order is organisationally mandated — KYC before decision before offer; no case worker may reorder it
- C) it's too long for CMMN
- D) CMMN lacks timers

<details><summary>Answer</summary>B — the litmus test applied. The capstone's
one discretionary pocket (fraud referral) is exactly where lesson 03's mixing
would enter.</details>

**Challenge.** Take three "too dynamic for BPMN" claims you've heard, or make
them up: dispute handling, hardship restructuring, high-value client
onboarding. Run the litmus test on each *step*, not each flow. The typical
finding: 80% of the "dynamic" flow is prescribed, with one genuinely
discretionary stage. That one stage is the shape lesson 03 models.

## Related

- Next: [Plan items, stages, milestones, sentries](../../02-plan-items-and-sentries/docs/en.md)
- The warning label: [lesson 04](../../04-when-cmmn-is-overkill/docs/en.md)
