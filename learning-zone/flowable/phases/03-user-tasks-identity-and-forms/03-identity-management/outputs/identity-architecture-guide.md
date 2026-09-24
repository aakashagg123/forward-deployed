---
name: identity-architecture-guide
description: Choosing an identity architecture for a process engine — three patterns and a migration checklist
kind: decision-guide
phase: 03
lesson: 03
---

# Identity & the engine — the one-page guide

## The rule

The engine **consumes** identity. The IdP **owns** it. Empty engine identity tables
are a healthy sign.

## Three architectures

| Pattern | Source of truth | When acceptable |
| :-- | :-- | :-- |
| Built-in IDM | engine tables | demos, tests, local Docker |
| Synced mirror | IdP, mirrored into engine | legacy investment already exists; accept sync lag |
| **Delegated (default)** | IdP; groups passed per request from token claims | production |

## The delegated pattern, concretely

1. User authenticates with the IdP; token carries `sub` + `groups` claims.
2. Your API layer (never raw `flowable-rest`) validates the token.
3. Task queries take the claim values as inputs:
   `taskCandidateGroupIn(claims.groups)`, `taskAssignee(claims.sub)`.
4. Claim and complete calls pass `claims.sub` as the acting user. The engine
   records it in the audit trail as an opaque ID.
5. Membership changes apply on the caller's next request — no sync.

## Contracts to protect

- [ ] Group names in models ↔ group claims in tokens: treat renames as breaking
      changes (alias during transition).
- [ ] Audit joinability: the IdP must resolve historical user IDs, including
      departed users, for as long as history retention (Phase 9) runs.
- [ ] Engine API perimeter: `flowable-rest`/engine APIs reachable only from your
      service layer, never from end-user clients.

## Migration off built-in IDM (checklist)

- [ ] Inventory group names referenced by deployed models (`candidateGroups`, IDM
      queries, expressions).
- [ ] Recreate them as IdP groups/claims with identical names first; rename later
      if desired, as a separate step.
- [ ] Switch authentication to the IdP; leave engine identity tables read-only.
- [ ] Re-point task queries to claim-driven inputs (delegated pattern).
- [ ] Run lesson 02's orphan sweep for tasks assigned to users absent from the IdP.
- [ ] Empty (or archive) the engine's user/group tables; alert if anything writes
      to them again.
