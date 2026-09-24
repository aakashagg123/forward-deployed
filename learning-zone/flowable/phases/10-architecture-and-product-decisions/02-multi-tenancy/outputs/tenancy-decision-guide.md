---
name: tenancy-decision-guide
description: Row / schema / stack tenancy decision dial with enforcement checklist
kind: decision-guide
phase: 10
lesson: 02
---

# Tenancy — the dial and the checklists

## Picking the stop

1. Any residency/"own database" clause? → **schema** minimum; runtime residency
   too → **stack**. (Non-negotiable — skip the rest.)
2. Tenants few, large, with divergent regulatory regimes? → **stack**.
3. Otherwise → **row tenancy**, with the enforcement checklist below in full.
4. Revisit per process: shared platform + one stack-tenant is normal, not
   failure.

## Row-tenancy enforcement checklist

- [ ] Tenant derived from token claims at the perimeter; never from request
      bodies or query params.
- [ ] One wrapper client injects `tenantId` into every engine query/command —
      raw engine access is lint-banned outside it.
- [ ] Deployments tagged at deploy time; starts inherit or set tenant explicitly.
- [ ] Cross-tenant admin operations behind a separate, audited role.
- [ ] Automated test: for each API route, tenant-A token requesting tenant-B
      resources gets 404/403 — run in CI, not in review.

## Shared vs per-tenant definitions (decide per process)

| Shared definition | Per-tenant deployments |
| :-- | :-- |
| one upgrade, one migration cohort plan | variants per partner |
| tenants move together (communicate!) | N × Phase 8 discipline |
| variant pressure → DMN tables keyed by tenant first | model forks only when DMN can't express the variance |

## Ops additions (Phase 9, tenant dimension)

- [ ] Probe signals grouped by tenant (dead letters, pools, oldest instance).
- [ ] Per-tenant throughput baseline — the noisy tenant must be visible.
- [ ] History retention (9.02) checked against *each* tenant's regime; the
      strictest ceiling wins on shared tables — or that tenant moves a stop up.
