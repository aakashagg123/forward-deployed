# Multi-tenancy: shared engine, shared tables, or neither

> **Motto** — Tenancy is an isolation-vs-cost dial with three stops — a tag column,
> a schema, or an engine — and regulation, not architecture taste, usually picks the
> stop.

*Part of Phase 10 — Architecture & product decisions. Concept lesson — no code
required.*

## The Problem

The platform works. Now the second brand, the second country, or the second
*bank partner* wants onboarding onto it. "Just add a tenant column" and "give
everyone their own stack" are both real answers, and they differ in cost by an
order of magnitude.

The wrong pick surfaces late — as an auditor's finding ("partner A's ops can
query partner B's loans") or a finance finding ("we run forty engines at 2%
utilisation"). Flowable supports three stops on the dial. The work is knowing
which failure you're buying.

## The Concept

<style>
.dgm-mt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mt-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-mt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-mt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-mt-chain{display:flex;flex-direction:column;gap:2px}
.dgm-mt-node{background:#faeceb;border:1.5px solid #e3b3ad;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#7a2c2e}
.dgm-mt-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-mt-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-mt{padding:20px 16px 18px}}
</style>
<div class="dgm-mt">
  <span class="dgm-mt-chip">Three tenancy models</span>
  <h4>Row, schema, or stack — isolation goes up as shared infrastructure goes down</h4>
  <p class="dgm-mt-sub">Each step costs more to run and buys more isolation between tenants.</p>
  <div class="dgm-mt-chain">
    <div class="dgm-mt-node alt">Row tenancy — one engine, one schema, TENANT_ID_ on every row</div>
    <div class="dgm-mt-arr">↓</div>
    <div class="dgm-mt-node accent">Schema tenancy — one engine process, datasource per tenant</div>
    <div class="dgm-mt-arr">↓</div>
    <div class="dgm-mt-node alt">Stack tenancy — engine per tenant</div>
  </div>
</div>


| | Row (tenant ID) | Schema per tenant | Stack per tenant |
| :-- | :-- | :-- | :-- |
| Isolation | logical only — every query must carry the tenant filter | hard at the data layer | hard everywhere |
| Blast radius | shared: one bad deploy/tenant storm hits all | shared compute, isolated data | none shared |
| Cost & ops | one of everything (cheapest) | one engine, N databases | N × Phase 9 |
| Per-tenant versions/models | shared definitions, or per-tenant deployments by tag | naturally per-tenant | trivially per-tenant |
| Fits | many small tenants, same product, no data-residency walls | regulated partners, residency, "your data in your database" contracts | few, large, paranoid tenants; different countries' stacks |

Here are the Flowable mechanics for the first stop, because it's the one with
sharp edges. Deployments, definitions, instances, tasks, and jobs all carry a
**tenant ID**. You set it at deployment (`.tenantId("partnerA")`) and at start
time, and you can filter on it in every query
(`taskCandidateGroupIn(...).taskTenantId("partnerA")`). The same key can be
deployed per tenant with different versions, giving you partner-specific process
variants without forking the platform.

The rules that keep each stop safe:

1. **Row tenancy stands or falls at the API layer.** The engine *stores* tenant
   IDs; it doesn't *enforce* them. Your perimeter (Phase 3.03's claims mapping:
   tenant comes from the token, never the request body) must inject the tenant
   filter into every query and command. One missed filter is a cross-tenant leak,
   so make it structurally impossible with a wrapper client, not a code-review
   rule.
2. **Shared vs per-tenant definitions is a product decision.** One shared model
   means one upgrade, and tenants move together (Phase 8 cohorts get a tenant
   dimension). Per-tenant deployments allow variants, but cost N migration
   projects. Pick per *process*, not platform-wide.
3. **Ops signals need the tenant dimension early.** Run Phase 9's probe per
   tenant, so one tenant's dead-letter storm or pool depth stays attributable.
   Otherwise the noisy tenant hides inside platform averages until they're
   everyone's problem.
4. **Residency trumps elegance.** A clause like "partner data stays in partner's
   database, in partner's country" ends the row-tenancy conversation regardless
   of cost. That's the schema or stack stop, by contract.

## Ship It

This lesson ships
[`outputs/tenancy-decision-guide.md`](../outputs/tenancy-decision-guide.md) — the
dial, the enforcement checklist for row tenancy, and the residency triggers.

## Check Yourself

**Q1.** Row tenancy's isolation is enforced by…

- A) the engine, automatically
- B) your API layer injecting the tenant (from token claims) into every query and command — the engine stores the tag, you enforce it
- C) the database
- D) the modeler

<details><summary>Answer</summary>B — the perimeter owns tenancy exactly as it
owns identity (Phase 3.03). Structural enforcement beats vigilance.</details>

**Q2.** A partner contract requires "our workflow data in our own database, in our
country". The dial stop is…

- A) row — add an index
- B) schema-per-tenant at minimum, stack if the runtime must be resident too — residency clauses end the shared-tables option
- C) encryption
- D) negotiable

<details><summary>Answer</summary>B — rule 4. Contracts and regulators pick this
stop; architecture just prices it.</details>

**Q3.** Deploying `loanOrigination` separately per tenant buys… at the cost of…

- A) nothing / nothing
- B) per-partner process variants / N versioning-and-migration projects instead of one (Phase 8, multiplied)
- C) speed / memory
- D) isolation / licenses

<details><summary>Answer</summary>B — variant freedom is real product value; its
price is every Phase 8 discipline times N. Choose per process.</details>

**Challenge.** Take the capstone platform and onboard two hypothetical tenants: a
sister brand (same product, same country) and a bank partner (residency clause,
custom review step). Place each on the dial. List the enforcement mechanics for
the first, and the migration-cost line for the second. You'll usually land on two
*different* stops — that's the mixed-tenancy reality most platforms run.

## Related

- Next: [Where the process ends and the domain begins](../../03-process-domain-boundary/docs/en.md)
- The perimeter that enforces it: [Phase 3, lesson 03](../../../03-user-tasks-identity-and-forms/03-identity-management/docs/en.md)
