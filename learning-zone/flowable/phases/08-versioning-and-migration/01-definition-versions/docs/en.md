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
.dgm-dv{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-dv-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-dv h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-dv-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-dv-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dgm-dv-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-dv-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-dv-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-dv-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-dv-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-dv-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-dv-col.neutral h6{color:#59636e}
.dgm-dv-col.accent h6{color:#7a2c2e}
.dgm-dv-col.blue h6{color:#0550ae}
.dgm-dv-col.green h6{color:#1a614f}
.dgm-dv-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-dv-item:last-child{margin-bottom:0}
.dgm-dv-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-dv{padding:20px 16px 18px}.dgm-dv-cols{grid-template-columns:1fr}}
.dgm-dv-note{margin-top:10px;padding:9px 14px;background:#faeceb;border:1px dashed #e3b3ad;border-radius:10px;
  font-size:10.5px;color:#7a2c2e;line-height:1.4}
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
