# Instance migration: moving live tokens to a new version

> **Motto** — Migration is a database change wearing a diagram: validate first, map
> every moved token explicitly, and rehearse on a copy before touching production.

*Part of Phase 08 — Versioning & migration.*

## The Problem

Lesson 01 left two versions executing side by side. That's fine when the old one
is merely *older*, but untenable when it's *wrong*: a compliance step was missing,
a routing condition was inverted, and four hundred in-flight applications carry
the defect. Draining — letting old instances finish on the old logic — is often
the right call. But when it isn't, because the regulator says the new step
applies to *everything in flight*, you need to move live tokens onto the new
definition without losing their position, variables, or history. That operation
is exactly as dangerous as it sounds. That is why the engine wraps it in a
ritual.

## The Concept

Migration re-points an instance's pinned definition and re-seats its tokens:

<style>
.dgm-imig{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-imig-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-imig h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-imig-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-imig-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-imig-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-imig-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-imig-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-imig-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-imig-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-imig-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-imig-col.neutral h6{color:#59636e}
.dgm-imig-col.accent h6{color:#7a2c2e}
.dgm-imig-col.blue h6{color:#0550ae}
.dgm-imig-col.green h6{color:#1a614f}
.dgm-imig-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-imig-item:last-child{margin-bottom:0}
.dgm-imig-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-imig{padding:20px 16px 18px}.dgm-imig-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-imig">
  <span class="dgm-imig-chip">Moving a running instance to a new definition</span>
  <h4>Migration maps the token's current activity to one on the new version</h4>
  <p class="dgm-imig-sub">The instance jumps straight to 'review' on v3 — it doesn't replay from the start.</p>
  <div class="dgm-imig-cols">
    <div class="dgm-imig-col neutral">
      <h6>v1 (defective)</h6>
      <div class="dgm-imig-item">Review 👤 ● → Approve</div>
    </div>
    <div class="dgm-imig-col accent">
      <h6>v3 (target)</h6>
      <div class="dgm-imig-item">Review 👤 ● → Compliance check ⚙️ (new) → Approve</div>
    </div>
  </div>
  <div class="dgm-imig-link">Migrate: token at 'review' → 'review' (same activity id)</div>
</div>


The mechanics, and where each risk lives:

1. **Auto-mapping by element ID.** A token at `review` lands on the target's
   `review` if an element with that ID exists. Unchanged IDs migrate for free.
   That is why lesson 04's checklist treats *renaming element IDs* as a breaking
   change.
2. **Explicit mappings for everything else.** If an element is removed, split, or
   renamed, you declare `fromActivityId → toActivityId`. With no mapping and no
   same-ID match, the migration is refused — the engine won't guess where a token
   belongs.
3. **Validation is a server-side dry run.** It reports unmappable tokens *without
   touching the instance*. This is the only sane first step, and the reason the
   client below never calls migrate without validate.
4. **What moves and what doesn't.** Variables ride along untouched. History keeps
   recording, so the instance's trail now spans two definitions — your audit
   narrative must say so. Timer subscriptions are re-created against the target
   where mapped. What migration does *not* do is run steps the instance already
   passed. Tokens sit where they sat — if the new compliance task is *upstream*
   of every live token, migrating changes nothing for them. Position migrates,
   not history.

Rule 4 is the strategic one. Migration answers "make future steps follow the new
diagram," not "apply the new policy retroactively." Retroactive fixes need a
batch job over history plus compensating actions (Phase 4), not a migration.

## Use It

[`code/migration_client.py`](../code/migration_client.py) scripts the ritual over
REST — find stragglers, validate + migrate each, verify:

```python
def migrate(instance_id, target_def_id, mappings=None):
    doc = {"toProcessDefinitionId": target_def_id}
    if mappings:
        doc["activityMigrationMappings"] = mappings
    call("POST", f"/runtime/process-instances/{instance_id}/migrate/validate", doc)
    call("POST", f"/runtime/process-instances/{instance_id}/migrate", doc)
    ...
```

Run it against lesson 01's leftovers:

```
$ python3 migration_client.py loanTriage
1 instance(s) not on latest (loanTriage:2:5211)
  migrated 90341  loanTriage:1:4007 -> latest

migrated 1, failed 0, remaining stragglers: 0
```

The client's failure branch is deliberate policy. Instances the validator refuses
get *skipped and reported*, never forced. Those are the ones needing explicit
mappings and a human decision. (In Java the same ritual is
`runtimeService.createProcessInstanceMigrationBuilder() ... .validateMigration() /
.migrate()`, plus batch variants for large populations.)

## Ship It

This lesson ships [`code/migration_client.py`](../code/migration_client.py) — the
validate → migrate → verify loop with straggler detection, the safe skeleton for
every real migration you'll run.

## Check Yourself

**Q1.** Why does the client always call validate before migrate?

- A) REST requires it
- B) validation is a server-side dry run that reports unmappable tokens without touching the instance — migrate-without-validate gambles production state on a guess
- C) it warms the cache
- D) it locks the instance

<details><summary>Answer</summary>B — same discipline as a database migration's dry
run. The validator is the only honest preview of where tokens land.</details>

**Q2.** v3 renamed `approve` to `approveLoan`. Migrating a token waiting at
`approve` requires…

- A) nothing; names are cosmetic
- B) an explicit mapping `approve → approveLoan` — auto-mapping matches element IDs only
- C) deleting the task first
- D) migrating twice

<details><summary>Answer</summary>B — IDs are the migration contract. That is why
gratuitous ID renames are the classic self-inflicted migration wound (lesson
04).</details>

**Q3.** The new mandatory compliance task sits *before* the review step where 400
tokens currently wait. After migrating all 400…

- A) each instance runs the compliance task immediately
- B) nothing visibly changes for them — tokens keep their position; the new task governs only paths not yet taken
- C) the tokens move back to the compliance task
- D) migration fails

<details><summary>Answer</summary>B — migration moves the pin, not the past.
Retroactive enforcement needs a batch of compensating actions, a different tool
entirely.</details>

**Challenge.** Break a migration on purpose: deploy a v3 of `loanTriage` with
`manualReview` renamed, park an instance at it, and run the client. Watch the
skip. Then add the mapping and re-run. Keep the failing validator output — it's
the error message you'll want to recognise at 2 a.m.

## Related

- Next: [Blue-green for processes](../../03-blue-green-for-processes/docs/en.md)
- Previous: [Definition versions](../../01-definition-versions/docs/en.md)
