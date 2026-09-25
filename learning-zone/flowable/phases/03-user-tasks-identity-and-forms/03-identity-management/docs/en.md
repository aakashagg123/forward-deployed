# Identity management: users, groups, and external IdPs

> **Motto** — The engine needs to know *who may act*. It should almost never decide
> *who exists* — that's your IdP's job.

*Part of Phase 03 — User tasks, identity & forms. Concept lesson — no code required.*

## The Problem

Candidate groups (lesson 02) quietly assumed somebody maintains the answer to "who is
in credit-ops?" Flowable ships a built-in identity store — user and group tables,
membership, even passwords. The demo-grade temptation is to use it: create users over
REST, and you're done. Six months later, HR moves three analysts and nobody updates
the engine's tables. Tasks route to ex-members, and security asks why a workflow
engine stores password hashes outside the corporate IdP. Identity is a *boundary*
decision, and the default should be that the engine consumes identity — it doesn't
own it.

## The Concept

Three architectures, in ascending order of seriousness:

<style>
.dgm-im{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-im-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-im h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-im-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-im-chain{display:flex;flex-direction:column;gap:2px}
.dgm-im-node{background:#faeceb;border:1.5px solid #e3b3ad;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#7a2c2e}
.dgm-im-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-im-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-im{padding:20px 16px 18px}}
</style>
<div class="dgm-im">
  <span class="dgm-im-chip">Three identity models</span>
  <h4>Who owns the truth about users and groups?</h4>
  <p class="dgm-im-sub">Each step moves ownership further away from the engine's own tables.</p>
  <div class="dgm-im-chain">
    <div class="dgm-im-node alt">1 · Built-in IDM — engine tables own users/groups</div>
    <div class="dgm-im-arr">↓</div>
    <div class="dgm-im-node accent">2 · Synced — IdP is the source of truth; engine tables are a mirror</div>
    <div class="dgm-im-arr">↓</div>
    <div class="dgm-im-node alt">3 · Delegated — engine stores no identity; groups arrive as claims per request</div>
  </div>
</div>


| | Built-in IDM | Synced | Delegated (recommended) |
| :-- | :-- | :-- | :-- |
| Source of truth | the engine | IdP (AD/Keycloak/Okta) | IdP |
| Engine stores | users, groups, passwords | mirrored users/groups | nothing (or key-only) |
| Membership change | manual API calls | sync-lag dependent | immediate — next request carries new claims |
| Auth | engine verifies passwords | IdP authenticates, engine authorizes | IdP issues tokens; your API layer maps claims → candidate groups |
| Honest use | demos, tests, this course's Docker image | legacy setups already invested | production |

The delegated pattern deserves a closer look because it's the one that surprises
people: **the engine never looks membership up**. Task queries take the group list as
an *input* — `candidateGroup in (...)`. Your API layer extracts groups from the
caller's token (OIDC claims) and passes them in with each request:

```
JWT claims: { sub: "asha", groups: ["credit-ops", "mumbai"] }
        ↓ your API layer
taskService.createTaskQuery().taskCandidateGroupIn(List.of("credit-ops", "mumbai"))
```

Membership changes in the IdP take effect on the next request. There's no sync job,
no stale mirror, no password storage. The engine's identity tables stay empty. What
it *does* keep is history — "claimed by asha" as an opaque string, joined back to a
real person by the IdP when an auditor asks.

Two design consequences:

1. **Group names become an API contract** between the IdP and the models.
   `flowable:candidateGroups="credit-ops"` must match a claim the IdP emits. Version
   and review group renames like the breaking changes they are.
2. **Authorization lives at your API layer**, not in the engine. The engine enforces
   task-level rules, like only the assignee can complete a task (lesson 01). Which
   tasks a caller may query at all is your perimeter to guard. Exposing
   `flowable-rest` directly to end users hands them an admin API, so it sits behind
   your service in every production topology (Phase 10).

## Ship It

This lesson ships
[`outputs/identity-architecture-guide.md`](../outputs/identity-architecture-guide.md).
It covers the three architectures, the claims-to-groups mapping pattern, and a
migration checklist off the built-in store.

## Check Yourself

**Q1.** In the delegated pattern, where does "asha is in credit-ops" live at query
time?

- A) the engine's membership tables
- B) in the request — extracted from her token's claims by your API layer and passed to the task query
- C) a nightly sync
- D) the model

<details><summary>Answer</summary>B — the engine consumes group lists and never
resolves membership itself. That inversion removes sync lag and password
custody.</details>

**Q2.** The IdP team renames `credit-ops` to `retail-credit-ops`. What breaks?

- A) nothing; names are cosmetic
- B) every deployed model whose candidateGroups references the old name — new tasks enter a pool nobody's claims match
- C) the engine crashes
- D) only new deployments

<details><summary>Answer</summary>B — group names are a cross-system contract.
Treat renames as breaking API changes: coordinate, alias during transition, or
migrate.</details>

**Q3.** What identity data *should* a production engine hold?

- A) users, groups, and hashed passwords
- B) essentially none — opaque user IDs in task/history fields, resolved to people by the IdP when needed
- C) a full LDAP mirror
- D) tokens

<details><summary>Answer</summary>B — the engine's job is workflow state and audit
references, not credential custody. Empty identity tables are a healthy
sign.</details>

**Challenge.** Sketch the claims-to-groups mapping for your own stack. Note which
token claim carries groups, where the mapping code sits, and what happens to an
in-flight task when its claimer is deactivated in the IdP mid-task (hint: lesson 02's
orphan runbook). If you can't answer the last one, that's the gap to close first.

## Related

- Next: [Forms](../../04-forms/docs/en.md)
- Perimeter topology: Phase 10, lesson 01 (see [`ROADMAP.md`](../../../../ROADMAP.md))
