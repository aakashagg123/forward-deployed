# Embedded vs standalone vs Flowable Work: deployment topologies

> **Motto** — Topology decides three things forever after: whose transaction the
> engine joins, who can call it, and who gets paged — choose it before the first
> model, not after the fiftieth.

*Part of Phase 10 — Architecture & product decisions. Concept lesson — no code
required. You've already *run* two of these: standalone in Phase 1, embedded in
Phase 2, lesson 05.*

## The Problem

Phase 2's comparison table settled the mechanics. What's left is the
organisational decision, and it's stickier than any technical one. Topology fixes
team boundaries (who owns models, who owns the engine), failure domains (whose
outage is a workflow outage), and upgrade politics (who schedules engine bumps).

Teams that let topology happen by accident — usually "embedded, because the
tutorial was" — discover the real constraints at the worst time: when the second
team wants in.

## The Concept

<style>
.dgm-dt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-dt-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-dt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-dt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-dt-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dgm-dt-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-dt-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-dt-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-dt-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-dt-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-dt-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-dt-col.neutral h6{color:#59636e}
.dgm-dt-col.accent h6{color:#7a2c2e}
.dgm-dt-col.blue h6{color:#0550ae}
.dgm-dt-col.green h6{color:#1a614f}
.dgm-dt-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-dt-item:last-child{margin-bottom:0}
.dgm-dt-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-dt{padding:20px 16px 18px}.dgm-dt-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-dt">
  <span class="dgm-dt-chip">Three shapes for the same engine</span>
  <h4>Embedded, standalone, or platform — the engine code barely changes</h4>
  <p class="dgm-dt-sub">What changes is the network hop and who else shares the deployment.</p>
  <div class="dgm-dt-cols">
    <div class="dgm-dt-col accent">
      <h6>Embedded — engine inside your service</h6>
      <div class="dgm-dt-item">Your Spring Boot app + engine library → your DB (app + ACT_* tables)</div>
    </div>
    <div class="dgm-dt-col blue">
      <h6>Standalone — engine as a service</h6>
      <div class="dgm-dt-item">Your services — REST → engine service → engine DB</div>
    </div>
    <div class="dgm-dt-col green">
      <h6>Platform — Flowable Work</h6>
      <div class="dgm-dt-item">Modelers, task UIs, admin, tenants → same engines underneath</div>
    </div>
  </div>
</div>


The decision table, with the rows that actually decide it on top:

| | Embedded | Standalone | Flowable Work |
| :-- | :-- | :-- | :-- |
| **Transactions** | joins yours — domain writes + token moves commit atomically (Ph. 2.05) | two systems; you engineer consistency | standalone's model |
| **Who can call it** | that JVM only | anything speaking HTTP | anything + shipped UIs |
| **Failure/paging domain** | your service *is* the engine | engine team owns a platform | vendor-supported platform |
| **Model ownership** | the owning team's repo | central repo/registry, review gates | Design's model repository |
| **Second-team cost** | a second engine+schema, or awkward sharing | near zero — that's the point | near zero |
| **Fits** | one product team, JVM, atomicity-critical (the capstone's natural home) | multi-team / polyglot platform play | buy-the-UIs decision (lesson 05) |

Rules of thumb that survive re-orgs:

1. **Count the teams, then decide.** One team, one JVM product means embedded,
   and you get the atomic commits. The moment a *second* team needs processes,
   embedded forks into engine-per-service (fine — separate schemas, separate
   upgrades) or flips to standalone. Decide which *before* the second team
   arrives.
2. **Never share one embedded engine's schema across services.** It welds their
   deploys, upgrades, and incidents together — the worst of both topologies. If
   you'd need a platform team to referee it, that's the sign you wanted
   standalone.
3. **Standalone's perimeter rule is absolute** (Phase 3.03): the engine API is an
   admin surface; it sits behind your services, never exposed to end clients.
4. **Mixed is legitimate at scale.** Core products embed for atomicity. Long-tail
   departmental flows share a standalone engine. Work enters if the UI/velocity
   trade (lesson 05) says buy.

## Ship It

This lesson ships
[`outputs/topology-decision-guide.md`](../outputs/topology-decision-guide.md) —
the table plus the team-count decision path.

## Check Yourself

**Q1.** The strongest *technical* argument for embedded is…

- A) fewer containers
- B) the engine joins your transaction — token moves and domain writes commit or roll back together (Phase 2's rules span your tables)
- C) faster REST
- D) no license

<details><summary>Answer</summary>B — atomicity is the one property no glue code
fully recovers once you split the transaction.</details>

**Q2.** Three product teams (one in Node) want workflows. The topology
conversation is really about…

- A) JSON serialization
- B) standing up standalone (or engine-per-JVM-team) — embedded can't serve the Node team, and sharing one embedded schema welds teams together
- C) rewriting in Java
- D) buying licenses

<details><summary>Answer</summary>B — team count and language mix are the real
inputs; rule 2 forbids the tempting shortcut.</details>

**Q3.** Flowable Work changes the topology question by…

- A) removing the engine
- B) adding shipped modelers/task UIs/admin on top of the standalone shape — it's a buy-the-UIs decision, not a new runtime model
- C) requiring Kubernetes
- D) making everything embedded

<details><summary>Answer</summary>B — the engines underneath are the ones you
learned; lesson 05 prices the layer above them.</details>

**Challenge.** Write the topology one-pager for your own organisation: team count
today and in 18 months, language mix, the flows where atomicity is
non-negotiable, and which rule of thumb bites first. If the answer is "mixed",
name the boundary line explicitly.

## Related

- Next: [Multi-tenancy](../../02-multi-tenancy/docs/en.md)
- The mechanics you already ran: [Phase 2, lesson 05](../../../02-the-engine-state-and-transactions/05-embedded-engine-spring-boot/docs/en.md)
