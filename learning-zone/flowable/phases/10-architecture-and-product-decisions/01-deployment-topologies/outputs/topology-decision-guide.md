---
name: topology-decision-guide
description: Embedded vs standalone vs Flowable Work — decision path and non-negotiable rules
kind: decision-guide
phase: 10
lesson: 01
---

# Topology — the decision path

1. **How many teams need processes, now and in 18 months?**
   - One, JVM → **embedded** (atomic commits are yours; capstone-shaped systems
     live here).
   - Several, or any non-JVM → 2.
2. **Do the teams' flows share data/transactions with their own domains
   heavily?**
   - Yes → **engine-per-team (embedded each)**: separate schemas, separate
     upgrade cadences.
   - No / mixed / platform-team appetite exists → **standalone** behind your API
     layer.
3. **Is the constraint actually UIs and modeling velocity, not runtime?**
   - Yes → price **Flowable Work** (lesson 05's worksheet) on top of the
     standalone shape.

## Non-negotiables (any topology)

- [ ] Never share one embedded engine's schema across services.
- [ ] Engine APIs are admin surfaces: behind your services, never end-client
      facing (Phase 3.03).
- [ ] Whoever owns the topology owns Phase 9: the probe, the retention decision,
      the restore drill — write the pager rota down as part of this decision.
- [ ] Model ownership and review path decided with the topology (repo per team
      vs central registry), not after the fiftieth model.

## Mixed-topology boundary (write yours)

Core atomic products: __________ (embedded).
Departmental/long-tail flows: __________ (standalone).
UI layer: build (Phase 3 clients) / buy (Work) — decided by: __________.
