---
name: retention-decision-guide
description: History level + retention worksheet — keep/archive/delete with PII checklist
kind: decision-guide
phase: 09
lesson: 02
---

# History level & retention — the worksheet

Fill one per process definition (defaults may differ per definition via
`flowable:historyLevel`).

## 1. Recording level

- [ ] Level chosen: `none | activity | audit | full` — and *why* in one sentence.
- [ ] `full` only with a named debugging window and a revert date.
- [ ] PII checklist:
  - [ ] No raw PAN/Aadhaar/account numbers as variables — references to the
        golden-record system instead.
  - [ ] Large payloads transient or externalised (Phase 2, lesson 02).
  - [ ] Form properties reviewed — they persist at `audit`+.

## 2. Retention windows

| Window | Value | Basis |
| :-- | :-- | :-- |
| Keep (queryable in engine DB) | ____ months | dashboards, disputes, ops queries |
| Archive (warehouse/lake) | ____ years | audit floor: regulator + Phase 8's audit sentence |
| Delete | after ____ years | compliance ceiling: DPDP/GDPR erasure basis |

- [ ] Floor ≥ every audit obligation; ceiling ≤ every erasure obligation; floor ≤ ceiling (if not, escalate — it's a legal conflict, not an engineering one).

## 3. Mechanics

- [ ] Cleanup: `flowable.enable-history-cleaning` + window, or a scheduled
      END_TIME_-based batch delete. Never START_TIME_; never open instances.
- [ ] Archive job runs *before* deletion and is verified (row counts reconcile).
- [ ] Deletion runs off-peak, batched, with the DBA's blessing on lock behaviour.

## 4. The standing metric

- [ ] Weekly: history growth rate vs cleanup throughput, alarmed when
      ingest > cleanup for 2 consecutive weeks.
