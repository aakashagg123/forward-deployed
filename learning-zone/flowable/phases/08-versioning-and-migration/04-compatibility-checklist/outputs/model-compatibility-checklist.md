---
name: model-compatibility-checklist
description: Pre-merge checklist for BPMN model changes — safe / mapping-needed / breaking
kind: checklist
phase: 08
lesson: 04
---

# Model change review — compatibility checklist

Run against every model PR while any instances of the key are live.

## Identity

- [ ] No element **ID** renamed (labels/names may change freely).
- [ ] No element deleted that a live token could currently occupy
      (check with lesson 8.01's population query before approving).
- [ ] Process **key** unchanged (a new key is a new product — that's a routing
      decision, 8.03, not a version).

## Variables (the invisible schema)

- [ ] Every newly-read variable has a null-tolerant default, a backfill plan, or a
      guarded path for pre-change instances.
- [ ] No variable removed or repurposed (name kept, meaning/type changed) while
      any live instance still writes or reads it.

## Gateways & flows

- [ ] Every exclusive gateway still has a default flow.
- [ ] New/changed conditions evaluated against *old* instances' data — no
      combination of pre-change variables can match zero flows.

## Timers, messages, errors

- [ ] Boundary events added are on existing IDs (safe) — none *removed* from
      activities where tokens may wait with armed subscriptions.
- [ ] Message names / error codes unchanged (they're cross-system contracts —
      Phase 7 lesson 03, Phase 4 lesson 03).

## If any box above failed

- [ ] Prefer the additive rewrite: new elements on new paths, old branch pruned
      after drain.
- [ ] Otherwise attach the migration note to the PR: explicit
      `fromActivityId → toActivityId` mappings, affected-population count, and the
      8.03 cohort strategy — the reviewer approves *that*, not just the diagram.
