# Definition versions: what a redeploy actually does

> **Motto** — A redeploy never changes a running process; it changes what *new*
> instances get — old tokens keep executing the diagram they started on.

*Part of Phase 08 — Versioning & migration. Concept reading:
[Principle 9 — instances outlive their definitions](../../../../foundations/process-automation-principles.md).*

## The Problem

You fix a gateway condition and redeploy. The dashboard still shows applications
taking the old path. Is that a bug? No — it is the most misunderstood *feature* in
BPM. Those instances started before your fix, and they are executing the
definition they started on. Without a precise model of versioning, you will either
"fix" things twice, or — worse — assume a compliance-mandated change reached
in-flight cases when it didn't. Every question in this phase reduces to one:
*which definition does this token read next?*

## The Concept

Deploying a model with an existing key doesn't replace anything — it appends:

<style>
.dgm-dv{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-danger-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-dv-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-danger-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-danger-solid) 28%, transparent)}
.dgm-dv h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-dv-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-dv-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dgm-dv-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-dv-col.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-dv-col.accent{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-dv-col.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-dv-col.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-dv-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-dv-col.neutral h6{color:var(--color-text-secondary)}
.dgm-dv-col.accent h6{color:var(--color-text-danger)}
.dgm-dv-col.blue h6{color:var(--color-text-info)}
.dgm-dv-col.green h6{color:var(--color-text-success)}
.dgm-dv-item{background:var(--color-surface);border:1px solid var(--color-border-info-surface);border-radius:8px;padding:6px 9px;font-size:10px;
  color:var(--color-text);line-height:1.35;margin-bottom:5px}
.dgm-dv-item:last-child{margin-bottom:0}
.dgm-dv-link{display:flex;justify-content:center;color:var(--color-text-tertiary);font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-dv{padding:20px 16px 18px}.dgm-dv-cols{grid-template-columns:1fr}}
.dgm-dv-note{margin-top:10px;padding:9px 14px;background:var(--color-background-danger-surface);border:1px dashed var(--color-border-danger-surface);border-radius:10px;
  font-size:10.5px;color:var(--color-text-danger);line-height:1.4}
</style>
<div class="dgm-dv">
  <span class="dgm-dv-chip">Three deployed versions, three bound instances</span>
  <h4>A running instance never moves versions on its own</h4>
  <p class="dgm-dv-sub">It binds to whatever was latest the moment it started — and stays there.</p>
  <div class="dgm-dv-cols">
    <div class="dgm-dv-col neutral">
      <h6>v1</h6>
      <div class="dgm-dv-item">loanTriage:1:4001</div>
    </div>
    <div class="dgm-dv-col blue">
      <h6>v2</h6>
      <div class="dgm-dv-item">loanTriage:2:5203</div>
    </div>
    <div class="dgm-dv-col accent">
      <h6>v3 (latest)</h6>
      <div class="dgm-dv-item">loanTriage:3:6104</div>
    </div>
  </div>
  <div class="dgm-dv-note">Instance started Jan 5 → binds to v1 · instance started Mar 2 → binds to v2 · new start today → binds to v3.</div>
</div>


Three rules carry everything:

1. **Redeploy means append.** Same key → version N+1, and old versions remain
   deployed and *executable*. The definition ID (`key:version:generated`) is the
   precise handle. The key alone means "latest" only at start time.
2. **Starts bind latest; instances pin forever.** `startProcessInstanceByKey`
   resolves the newest version *at that moment*. The instance then stores that
   definition ID and reads it for every subsequent step, wait state, and timer.
3. **Simultaneous versions are normal.** A 90-day mortgage process under weekly
   deploys means roughly 13 versions live at once. That's not mess — it's the
   engine keeping Phase 2's promise that persisted state must keep meaning what it
   meant.

Here are the consequences people trip on. Version-pinning applies to *everything*
attached to the definition: timers fire into the old diagram, and DMN references
resolve per the old task config. History rows record the version that ran — that's
your audit answer. And the repository grows monotonically. Cleaning up truly-dead
old versions is a deliberate operational act (Phase 9), never automatic.

## Use It

[`code/versions_client.py`](../code/versions_client.py) makes the rules observable —
deploy Phase 1's model twice, park an instance under each:

```
$ python3 versions_client.py
after 1st deploy: [(1, 'loanTriage:1:4007')]
after 2nd deploy: [(2, 'loanTriage:2:5211'), (1, 'loanTriage:1:4007')]

new start binds latest : True
old instance still pinned: True

-> two live instances of one key, on two definitions. Moving the old one is
   MIGRATION (lesson 02); until then both versions execute.
```

Two operational notes follow directly. Deploys are cheap and additive, so
deploy-often is safe *for new starts* — the risk lives entirely in forgetting the
pinned population. And if a bad version ships, you can suspend *that definition
version* (`repository/process-definitions/{id}` with `action: suspend`) to stop
new starts on it while good versions keep serving.

## Ship It

This lesson ships [`code/versions_client.py`](../code/versions_client.py) — the
three rules as a runnable proof, and the query helpers (`versions`, pinned-instance
lookup) that lesson 02's migration client builds on.

## Check Yourself

**Q1.** A compliance change deploys as v5. Applications started under v4 are…

- A) automatically on v5
- B) still executing v4 — the change reaches them only via migration (or by draining)
- C) suspended
- D) failed

<details><summary>Answer</summary>B — rule 3. If the regulator's change must reach
in-flight cases, redeploying is only half the job. Lesson 02 is the other
half.</details>

**Q2.** A timer armed under v2 fires after v6 ships. Which diagram does the token
continue in?

- A) v6 — latest wins
- B) v2 — the instance's pinned definition, timers included
- C) whichever the job executor picks
- D) it errors

<details><summary>Answer</summary>B — pinning covers every deferred continuation:
timers, messages, async jobs all resume into the version the instance
carries.</details>

**Q3.** `startProcessInstanceByKey("loanTriage")` chooses a version…

- A) randomly among deployed versions
- B) the latest at the moment of the call; the choice is then frozen into the instance
- C) configured globally
- D) v1 always

<details><summary>Answer</summary>B — keys resolve at start time only. Everything
after start speaks definition IDs.</details>

**Challenge.** Extend the client with `population(key)`: for each deployed version,
print the live-instance count and oldest start date. That one table — "who is
still on v1 and since when" — is the input every migration decision (lesson 02)
and every version-cleanup decision (Phase 9) starts from.

## Related

- Next: [Instance migration](../../02-instance-migration/docs/en.md)
- Why pinning exists at all: [Phase 2, lesson 01](../../../02-the-engine-state-and-transactions/01-wait-states-and-persistence/docs/en.md)
