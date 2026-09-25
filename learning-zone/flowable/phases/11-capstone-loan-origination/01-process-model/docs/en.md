# Capstone 01 — The process model: application → decision → offer → disbursal

> **Motto** — Nothing in this model is new; the capstone is the proof that the pieces
> compose.

*Part of Phase 11 — Capstone. Combines Phases 1, 3, 4, 7.*

## The Project

One process —
[`outputs/loan-origination.bpmn20.xml`](../outputs/loan-origination.bpmn20.xml) —
carrying a loan application from arrival to disbursal, decline, or expiry:

<style>
.dgm-cap{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-cap-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-cap h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-cap-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-cap-chain{display:flex;flex-direction:column;gap:2px}
.dgm-cap-node{background:#faeceb;border:1.5px solid #e3b3ad;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#7a2c2e}
.dgm-cap-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-cap-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-cap{padding:20px 16px 18px}}
.dgm-cap-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-cap-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-cap-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-cap-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-cap-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-cap-b.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-cap-b.accent h6{color:#7a2c2e}
.dgm-cap-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-cap-b.blue h6{color:#0550ae}
.dgm-cap-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-cap-b.green h6{color:#1a614f}
.dgm-cap-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-cap-b.red h6{color:#82061e}
.dgm-cap-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-cap-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-cap{padding:20px 16px 18px}.dgm-cap-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-cap">
  <span class="dgm-cap-chip">Capstone: loan origination, end to end</span>
  <h4>One process, four decision points, three ways to end</h4>
  <p class="dgm-cap-sub">Bureau pull and KYC review run in parallel; everything else is sequential.</p>
  <div class="dgm-cap-chain">
    <div class="dgm-cap-node alt">● Start → fork</div>
  </div>
  <div class="dgm-cap-q">Parallel branches</div>
  <div class="dgm-cap-branches" style="grid-template-columns:repeat(2,1fr)">
    <div class="dgm-cap-b blue">
      <h6>Bureau pull 🌐 (async)</h6>
      <p>⚡ error → manual bureau pull 👤</p>
    </div>
    <div class="dgm-cap-b accent">
      <h6>KYC review 👤</h6>
      <p>Runs alongside the bureau pull</p>
    </div>
  </div>
  <div class="dgm-cap-chain">
    <div class="dgm-cap-node alt">Join</div>
  </div>
  <div class="dgm-cap-q">KYC ok?</div>
  <div class="dgm-cap-branches" style="grid-template-columns:repeat(2,1fr)">
    <div class="dgm-cap-b red">
      <h6>No → ● rejected</h6>
    </div>
    <div class="dgm-cap-b green">
      <h6>Yes → continue</h6>
      <p>Credit decision 📋 DMN</p>
    </div>
  </div>
  <div class="dgm-cap-q">Decision?</div>
  <div class="dgm-cap-branches">
    <div class="dgm-cap-b green">
      <h6>Auto-approve</h6>
      <p>→ Accept offer 👤 ⏰ P30D</p>
    </div>
    <div class="dgm-cap-b accent">
      <h6>Manual review</h6>
      <p>Credit review 👤 → approve or decline</p>
    </div>
    <div class="dgm-cap-b red">
      <h6>Decline</h6>
      <p>→ ● declined</p>
    </div>
  </div>
  <div class="dgm-cap-q">Offer outcome</div>
  <div class="dgm-cap-branches" style="grid-template-columns:repeat(2,1fr)">
    <div class="dgm-cap-b green">
      <h6>Accepted</h6>
      <p>Disburse ⚙️ → ● disbursed</p>
    </div>
    <div class="dgm-cap-b neutral">
      <h6>⏰ Expired (P30D)</h6>
      <p>→ ● expired</p>
    </div>
  </div>
</div>


Every element cites its lesson:

| Element | Built in |
| :-- | :-- |
| parallel fork/join over bureau + KYC | Phase 1, lesson 02 |
| async HTTP bureau task, failure → BPMN error → manual fallback | Phase 4, lessons 02/04; Phase 2, lesson 03 |
| candidate groups + form properties on every human task | Phase 3, lessons 02/04 |
| `flowable:type="dmn"` decision task, gateway routing on `${decision}` | Phase 5, lesson 03 |
| interrupting offer-expiry timer, duration from `${offerValidity}` | Phase 7, lesson 01 |

Three composition decisions worth defending in review:

1. **The bureau task is async** (`flowable:async="true"`). A third-party call must
   not hold the start transaction hostage, and retries come free (Phase 2's
   rules). Its *error* path is a designed fallback, not an incident.
2. **KYC gate before the decision task.** There's no point pricing a file that
   fails KYC. Ordering checks by cost and kill-probability is process design,
   not engine mechanics.
3. **Offer validity is a variable**, not a literal `P30D`. The value can migrate
   into the DMN table later without touching the model (Phase 5's governance
   boundary).

## Verify It

```bash
python3 - <<'PY'
import xml.dom.minidom; xml.dom.minidom.parse(
  "flowable/phases/11-capstone-loan-origination/01-process-model/outputs/loan-origination.bpmn20.xml")
print("well-formed")
PY
```

Then deploy and run it — that's [lesson 03](../../03-the-driver/docs/en.md); the
decision table it references is [lesson 02](../../02-credit-decision-table/docs/en.md).

**Challenge.** Add the two Phase 7 event subprocesses from
[lesson 7.05](../../../07-events-timers-and-messaging/05-event-subprocesses/docs/en.md)
— interrupting `customerWithdrawal`, non-interrupting weekly nudge — and re-verify.
The diff should be purely additive: that's the composition property working.
