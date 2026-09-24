# Backward-compatible model changes: a checklist

> **Motto** — Migration pain is chosen at *editing* time: model changes made with the
> pinned population in mind migrate for free; careless ones cost a mapping document
> each.

*Part of Phase 08 — Versioning & migration. Concept lesson — no code required.*

## The Problem

Phases 8.01–8.03 dealt with versions after the fact. But the cost of every future
migration is set earlier, in the modeler, the moment someone "tidies up" element
IDs, deletes a task that tokens might occupy, or renames a variable. Each of those
edits is invisible in review ("the diagram looks the same!") and turns the next
deploy from *drain quietly* into *migration project*. Teams need the same
instinct database engineers have about column renames. It fits on one page.

## The Concept

Every edit sorts into three buckets by what it does to the pinned population and
lesson 02's auto-mapping:

| Bucket | Edits | Cost |
| :-- | :-- | :-- |
| **Safe** (auto-migrates, drain works) | add activities on new paths; add boundary events/event subprocesses; widen gateway conditions; change expressions, forms, assignments *on existing IDs*; add optional variables | none |
| **Mapping needed** | rename element IDs; replace a task with a different one; split one activity into two; move activities across subprocess boundaries | explicit `from → to` per edit, forever (until that population drains) |
| **Breaking** (mapping can't save you) | delete an activity tokens may occupy; remove a variable later steps read; repurpose a variable's meaning/type; narrow a gateway so old data matches nothing; remove the default flow | redesign the change, or accept stuck/misrouted instances |

The deeper rules behind the buckets:

1. **Element IDs are your ABI.** The diagram is the code (Principle 2), and IDs
   are its stable symbols. Auto-mapping (8.02), history queries, and timer
   re-seating all key on them. Rename labels freely, but never rename IDs —
   cosmetic ID renames are the #1 self-inflicted migration.
2. **Variables are a schema without a migrator.** The engine maps *positions*,
   not data. A v5 step reading `employmentType` finds nothing in a v1-started
   instance that never wrote it. Every new read needs a default
   (`${employmentType ?? 'salaried'}`), a backfill, or a guard — exactly like a
   nullable column with no `DEFAULT`.
3. **Additive beats mutative.** Need different behaviour at `review`? Add
   `reviewV2` on a new path and route to it. Old tokens keep a valid home, new
   instances take the new road, and you delete the old branch a quarter later
   once the population drains. Two small versions beat one clever one.
4. **Gateways must stay total for *old* data.** New conditions get evaluated
   against variables written under old versions. Every exclusive gateway keeps
   a default flow, and conditions must tolerate missing variables — Phase 1's
   dead-instance rule, now with a time dimension.

## Ship It

This lesson ships
[`outputs/model-compatibility-checklist.md`](../outputs/model-compatibility-checklist.md)
— the three buckets as a pre-merge checklist for model review, closing the phase:
versions (what a deploy does), migration (how tokens move), rollout (which cohorts),
and now compatibility (how to rarely need any of it).

## Check Yourself

**Q1.** Renaming a userTask's *label* vs its *ID*:

- A) both are cosmetic
- B) label is free; the ID rename converts every future migration of live tokens at that task into an explicit-mapping exercise
- C) both are breaking
- D) IDs can't be renamed

<details><summary>Answer</summary>B — IDs are the migration contract and the history
key. Labels are for humans; IDs are for the engine.</details>

**Q2.** v6 adds a step reading `employmentType`, which pre-v6 instances never wrote.
Safe deployment requires…

- A) nothing — the engine defaults it
- B) a null-tolerant expression, a backfill of old instances, or a guarded path — a variable read is a schema dependency
- C) migrating everyone first
- D) deleting old instances

<details><summary>Answer</summary>B — positions migrate, data doesn't. Treat new
variable reads like adding a NOT NULL column: supply the default
yourself.</details>

**Q3.** The team wants `review` to behave completely differently. The
lowest-total-cost edit is usually…

- A) rewrite `review` in place
- B) add `reviewV2` on a new path, route new instances to it, delete the old branch after the population drains
- C) delete `review` and migrate with mappings
- D) a new process key

<details><summary>Answer</summary>B — additive-then-prune keeps every live token
housed and makes the eventual cleanup a safe deletion of an *empty*
branch.</details>

**Challenge.** Diff the capstone model against a hypothetical v2 that (a) renames
`creditReview` to `seniorCreditReview`, (b) adds a fraud-check service task before
the DMN call, and (c) starts reading a new `channel` variable at the route gateway.
Bucket each edit, write the mapping/default it demands, and state which cohort
strategy (8.03) the combined change forces. That's the whole phase in one exercise.

## Related

- Phase README: [Versioning & migration](../../README.md)
- The mapping mechanics these buckets feed: [Instance migration](../../02-instance-migration/docs/en.md)
