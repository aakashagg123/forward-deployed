# History levels & data growth: the retention decision

> **Motto** — History is the only table family with no natural ceiling: choose what
> you record and how long you keep it *on purpose*, or the database chooses an outage
> for you.

*Part of Phase 09 — Operations & observability. Concept lesson — no code required.*

## The Problem

The Docker image and Phase 2's starter both run `history-level=full`. That's right
for learning, but it's a default nobody revisits. A loan book doing 50k
applications a month writes millions of ACTINST and VARINST rows. Two years later,
the history tables dwarf runtime a thousandfold, dashboards slow down, and backups
balloon. At the sharp end, the DPO asks why customer PAN values still sit in
`ACT_HI_VARINST` seven years past any retention basis.

Recording level and retention window are one decision with three stakeholders: ops
(query speed), finance (storage), and compliance (a floor *and* a ceiling on
keeping data).

## The Concept

**Lever 1 — what gets written** (`flowable.history-level`):

| Level | Records | Honest use |
| :-- | :-- | :-- |
| `none` | nothing | pure-throughput engines where an external system owns audit |
| `activity` | instances + steps, **no variables** | metrics without payload custody — underrated for PII-heavy domains |
| `audit` (engine default) | + variable values, form properties | the usual regulated-flow answer |
| `full` | + variable *updates* (every intermediate value) | debugging, courses, never high-volume production by accident |

Two refinements help before you drop a level globally. A per-definition override
(`flowable:historyLevel` on the process) keeps `audit` for the loan book while the
notification workflow runs `activity`. And **transient variables** (Phase 2), plus
"store a document *reference*, not the document," solve most PII-in-history
findings without touching the level.

**Lever 2 — how long it stays.** Growth is `rate × record size × retention`, and
retention is the only lever that bounds it:

<style>
.dgm-hl{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-hl-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-hl h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-hl-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-hl-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-hl-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-hl-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-hl-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-hl-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-hl-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-hl-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-hl-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-hl{padding:20px 16px 18px}.dgm-hl-row{flex-direction:column}}
</style>
<div class="dgm-hl">
  <span class="dgm-hl-chip">From written to deleted</span>
  <h4>History has a lifecycle too — it isn't kept forever by default</h4>
  <p class="dgm-hl-sub">The compliance ceiling, not disk space, is usually what ends it.</p>
  <div class="dgm-hl-row">
    <div class="dgm-hl-n ">Written — at the chosen history level</div>
    <span class="dgm-hl-arr">→</span>
    <div class="dgm-hl-n accent">Kept — the query window (dashboards, disputes, audits)</div>
    <span class="dgm-hl-arr">→</span>
    <div class="dgm-hl-n blue">Archived — exported to warehouse/lake (cheap, joinable, immutable)</div>
    <span class="dgm-hl-arr">→</span>
    <div class="dgm-hl-n red">Deleted — past the compliance ceiling (DPDP/GDPR erasure basis ends)</div>
  </div>
</div>


The floor comes from audit and regulatory obligations — Phase 8's audit sentence
must stay answerable. The ceiling comes from data-protection law: *keeping
everything forever is a compliance failure in the other direction.*

Mechanically, use Flowable's built-in history-cleaning job
(`flowable.enable-history-cleaning=true` plus a `history-cleaning-after` window),
or scheduled batch deletes keyed on `END_TIME_`. Always key on end time, never
touch open instances, and always archive before you delete if the warehouse is the
system of record for old cases.

**The one metric:** history growth per week, plotted against the deletion job's
throughput. If ingest exceeds cleanup, the ceiling is just an outage with a date.

## Ship It

This lesson ships
[`outputs/retention-decision-guide.md`](../outputs/retention-decision-guide.md) —
the level table, the keep/archive/delete worksheet, and the PII checklist.

## Check Yourself

**Q1.** Metrics matter, but variables carry PAN/Aadhaar and an external system holds
the golden record. Best global level?

- A) full
- B) activity — timelines and durations without variable custody; references over payloads where audit needs data
- C) none
- D) audit

<details><summary>Answer</summary>B — the level is a data-custody decision, not a
debugging convenience. Record what you're prepared to protect.</details>

**Q2.** Why is retention both a floor and a ceiling?

- A) it isn't; longer is safer
- B) audit obligations set a minimum keep; data-protection law sets a maximum — past the erasure basis, keeping is the violation
- C) storage pricing
- D) the engine enforces 7 years

<details><summary>Answer</summary>B — "keep everything forever" fails DPDP/GDPR
exactly the way "delete after a month" fails the auditor.</details>

**Q3.** History cleanup jobs key on…

- A) START_TIME_
- B) END_TIME_ — only closed instances age out; an open 3-year-old mortgage keeps its full trail
- C) row count
- D) table size

<details><summary>Answer</summary>B — retention clocks start at completion. Open
instances are runtime's concern, and their history must survive them.</details>

**Challenge.** Fill the worksheet for the capstone: level per definition, keep
window, archive target, and deletion basis. Then compute the steady-state row
count at 50k applications a month and check it against your database sizing
(lesson 05). If the number surprises you, that was the point.

## Related

- Next: [Async executor tuning](../../03-executor-tuning/docs/en.md)
- The tables being governed: [History tables](../../01-history-tables/docs/en.md)
