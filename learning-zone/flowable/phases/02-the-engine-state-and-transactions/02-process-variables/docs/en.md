# Process variables & scope

> **Motto** — Variables are the instance's working memory. Scope decides which
> branch of the process can see — and silently overwrite — what.

*Part of Phase 02 — The engine: state & transactions.*

## The Problem

So far our variables were one flat dict per instance. That works until the
process forks. Two parallel branches both keep an `attempt` counter, or both
write their result to `result`, and the last writer silently wins. In a loan
process, that can mean the KYC branch's status overwrites the credit branch's —
a bug that shows up as "sometimes approvals have the wrong reason code" and
takes a week to trace, because nothing ever throws an error.

## The Concept

Engines solve this the way programming languages do: **lexical scoping over the
execution tree**. Every token or execution is a scope with a parent, and the
process instance is the root.

<style>
.dgm-pv{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pv-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-pv h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pv-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pv-chain{display:flex;flex-direction:column;gap:2px}
.dgm-pv-node{background:#faeceb;border:1.5px solid #e3b3ad;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#7a2c2e}
.dgm-pv-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-pv-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-pv{padding:20px 16px 18px}}
.dgm-pv-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-pv-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-pv-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pv-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-pv-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pv-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-pv-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-pv-col.neutral h6{color:#59636e}
.dgm-pv-col.accent h6{color:#7a2c2e}
.dgm-pv-col.blue h6{color:#0550ae}
.dgm-pv-col.green h6{color:#1a614f}
.dgm-pv-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-pv-item:last-child{margin-bottom:0}
.dgm-pv-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-pv{padding:20px 16px 18px}.dgm-pv-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-pv">
  <span class="dgm-pv-chip">Variable scoping</span>
  <h4>Each branch gets its own private copy of local variables</h4>
  <p class="dgm-pv-sub">Reading walks up to instance scope; writing to a local name never leaks across branches.</p>
  <div class="dgm-pv-chain">
    <div class="dgm-pv-node accent">Instance scope — applicant, amount</div>
  </div>
  <div class="dgm-pv-cols">
    <div class="dgm-pv-col blue">
      <h6>Credit branch scope</h6>
      <div class="dgm-pv-item">attempt (local)</div>
    </div>
    <div class="dgm-pv-col green">
      <h6>KYC branch scope</h6>
      <div class="dgm-pv-item">attempt (local)</div>
    </div>
  </div>
</div>


Three rules apply identically in the toy build and in Flowable:

1. **Read**: walk up the chain. The nearest declaration wins.
2. **Write** (`setVariable`): update the scope that declares the name. If none
   does, declare it at the **root**, so results written from a branch survive
   the join.
3. **Local write** (`setVariableLocal`): pin the name to the current scope.
   Siblings can't see it, and it dies when the branch joins.

Rule 2 is the sharp edge. Because undeclared writes float to the root, *two
parallel branches writing the same name overwrite each other silently*. The
discipline that prevents it: keep branch-internal working state local, and give
instance-level results distinct names.

Two Flowable-specific facts are worth knowing early:

- **Variables are typed rows** (`ACT_RU_VARIABLE`). Strings, numbers, and dates
  are native types; anything else gets serialised (JSON or Java serialization).
  Big blobs in variables are a classic performance smell — store a reference
  (a document ID), not the document itself.
- **Transient variables** exist for exactly one purpose: pass a payload to the
  next few steps without ever persisting it. They live only until the next
  wait state.

## Build It

[`code/variables.py`](../code/variables.py) — a parent-chained scope in ~40
lines. The whole semantics lives in `set`:

```python
def set(self, key, value):
    scope = self
    while scope:
        if key in scope.vars:
            scope.vars[key] = value
            return
        if scope.parent is None:
            scope.vars[key] = value       # new variable -> process instance level
            return
        scope = scope.parent
```

The demo builds the fork above and walks straight into the classic bug:

```
$ python3 variables.py
instance sees result = kyc-ok  <- last writer won
instance variables: {'applicant': 'meera', 'amount': 500000, 'score': 720, ...}
```

## Use It

Here are the same three operations in Flowable's API — the same semantics you
just built:

```java
runtimeService.setVariable(executionId, "score", 720);        // walks up, roots if new
runtimeService.setVariableLocal(executionId, "attempt", 1);   // pinned to this execution
runtimeService.getVariable(executionId, "score");             // walks up

// and in a delegate:
execution.setTransientVariable("bureauPayload", bigJson);     // never persisted
```

Over REST, task completion writes instance-level variables by default. Add
`"scope": "local"` to a variable to pin it:

```json
{"action": "complete",
 "variables": [{"name": "attempt", "value": 2, "scope": "local"}]}
```

## Ship It

This lesson ships the scope chain as a module:
[`code/variables.py`](../code/variables.py). You'll reuse this mental model every
time you read a Flowable stack trace containing `VariableScopeImpl`.

## Check Yourself

**Q1.** A parallel branch calls `setVariable("status", "ok")` and no scope declares
`status`. Where does it land?

- A) the branch's local scope
- B) the process instance (root) scope
- C) it errors — undeclared variable
- D) a random scope

<details><summary>Answer</summary>B — undeclared writes float to the root. This is
useful for returning results past the join, and dangerous when two branches
pick the same name.</details>

**Q2.** Two parallel branches each need a retry counter. Correct pattern?

- A) `setVariable("attempt", n)` in both
- B) `setVariableLocal("attempt", n)` in each branch
- C) one shared counter with a prefix
- D) store it in a database table outside the engine

<details><summary>Answer</summary>B — branch-internal working state is exactly what
local scope is for. The counters can't clobber each other, and they vanish at
the join.</details>

**Q3.** You need to pass a 2 MB bureau response from one service task to the next, and
never want it in the database. Use…

- A) a normal variable
- B) a local variable
- C) a transient variable
- D) a file on disk

<details><summary>Answer</summary>C — transient variables live only until the next
wait state and are never persisted. (Even better: store the document elsewhere
and pass its ID.)</details>

**Challenge.** Extend the toy `Scope` with `destroy()`: when a branch scope dies
at a join, its local variables vanish, but anything it wrote to the root
survives. Then write the failing test first — both branches `set("result", ...)`,
join, and assert the root holds *both* results. Watch it fail, then fix the
model, not the engine, by renaming.

## Related

- Next: [Transaction boundaries & async continuations](../../03-transactions-and-async/docs/en.md)
- Previous: [Wait states & persistence](../../01-wait-states-and-persistence/docs/en.md)
