---
name: decision-governance-checklist
description: Per-table governance card — ownership, change ritual, validation, audit
kind: decision-guide
phase: 05
lesson: 04
---

# Decision governance — the per-table checklist

Fill one card per deployed decision table. A table that can't fill this card
shouldn't be in production.

## Card: `<table key>`

**1. Ownership**
- [ ] Accountable owner (one name): ____________
- [ ] UNIQUE-violation / no-match alerts route to the owner, not ops
- [ ] Backup owner named for leave/attrition

**2. Change ritual**
- [ ] Changes proposed as table diffs (row-level), never console edits
- [ ] Approval: owner + one reviewer minimum; committee sign-off where mandated
- [ ] Deployed as a new version via the same CI as process models
- [ ] Production consoles are read-only for everyone

**3. Validation (gates the deploy)**
- [ ] Golden cases file exists and passes (input → expected output pairs)
- [ ] Structural checks: overlap (UNIQUE), completeness, cell types
- [ ] Impact replay: last N days' real inputs through old vs new version, diff
      reviewed ("flips X% of cases from A to B")

**4. Audit**
- [ ] History records the table version behind every decision (retention per
      Phase 9 policy)
- [ ] Regulated flows pin in-flight instances to their starting version (Phase 8)
- [ ] Approved-policy document ↔ deployed-version mapping is maintained

## Scope check (before any of the above)

- [ ] This is *policy the business tunes* (threshold/band/grid/eligibility), not an
      algorithm, validation, or anything needing loops, calls, or state — those stay
      in code.
