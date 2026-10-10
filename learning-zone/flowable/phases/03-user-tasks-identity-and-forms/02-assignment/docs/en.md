# Assignment: assignee, candidate users, candidate groups

> **Motto** — Assign roles, not people. `assignee="ravi"` is an outage waiting for
> Ravi's resignation letter. `candidateGroups="credit-ops"` survives every org chart.

*Part of Phase 03 — User tasks, identity & forms.*

## The Problem

Every user task must answer one question: whose inbox does this land in? The model
writes the answer, so a bad answer gets deployed. The classic failure is hard-coding
a person. The task `flowable:assignee="ravi"` works fine until Ravi goes on leave,
transfers, or leaves the company. Then live instances sit in the inbox of someone who
will never come back, and fixing it means migrating instances or editing task state
by hand. Assignment is a modelling decision with real operational risk.

## The Concept

Three attributes, in order of preference — *later in this list = more fragile*:

| Attribute | Semantics | Use when |
| :-- | :-- | :-- |
| `flowable:candidateGroups` | task enters the group's **pool**; any member may claim | the default — teams own queues |
| `flowable:candidateUsers` | pool limited to named individuals | rare: a fixed pair of signatories |
| `flowable:assignee` | pre-claimed, skips the pool entirely | truly personal work ("the applicant uploads *their* documents") — and then almost always an **expression**, not a literal |

<style>
.dgm-asg{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-danger-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-asg-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-danger-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-danger-solid) 28%, transparent)}
.dgm-asg h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-asg-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-asg-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-asg-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-asg-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-asg-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-asg-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-asg-b.accent{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-asg-b.accent h6{color:var(--color-text-danger)}
.dgm-asg-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-asg-b.blue h6{color:var(--color-text-info)}
.dgm-asg-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-asg-b.green h6{color:var(--color-text-success)}
.dgm-asg-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-asg-b.red h6{color:var(--color-text-danger)}
.dgm-asg-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-asg-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-asg{padding:20px 16px 18px}.dgm-asg-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-asg">
  <span class="dgm-asg-chip">How a task finds its first owner</span>
  <h4>Assignee set on creation, or open to a pool?</h4>
  <p class="dgm-asg-sub">Either way, only one person ends up holding it — CLAIMED.</p>
  <div class="dgm-asg-q">Task created — assignee set?</div>
  <div class="dgm-asg-branches">
    <div class="dgm-asg-b green">
      <h6>Yes</h6>
      <p>Lands directly in that person's list (CLAIMED)</p>
    </div>
    <div class="dgm-asg-b accent">
      <h6>No</h6>
      <p>Enters candidate pool(s), unassigned (CREATED) — first claim wins, moves to CLAIMED</p>
    </div>
  </div>
</div>


Two refinements that keep models clean:

1. **Expressions over literals, always.** Use `flowable:assignee="${applicant}"`
   (the instance knows who applied) or `flowable:candidateGroups="${region}-credit-ops"`
   (routing by data). The model states the *rule*, and identity data supplies the
   names at runtime.
2. **Pools compose with the lifecycle.** A claimed task leaves the pool queries —
   that's lesson 01's race, visible in the API. Unclaim returns the task to the pool.
   The pool *is* the backlog view, which is why lesson 05 builds the whole inbox on
   two queries.

## Use It

[`code/assignment_client.py`](../code/assignment_client.py) drives the protocol
against Phase 1's `loanTriage`. Its review task declares
`flowable:candidateGroups="credit-ops"`. Two queries matter:

```python
def group_pool(group):
    """The unclaimed pool for a group: candidate tasks with no assignee yet."""
    return call("POST", "/query/tasks", {
        "candidateGroup": group, "unassigned": True, "size": 50,
    }).get("data", [])

def my_tasks(user):
    return call("POST", "/query/tasks", {"assignee": user, "size": 50}).get("data", [])
```

And the run shows the race from lesson 01, now with HTTP semantics:

```
$ python3 assignment_client.py
credit-ops pool: [('Manual credit review', '7512')]
asha claimed 7512
ravi refused: HTTP 409 (already claimed)
asha's list : ['7512']
pool now    : []
completed; instance ended: True
```

The 409 is lesson 01's `TransitionError` on the wire — same guarantee, same reason.

## Ship It

This lesson ships
[`outputs/assignment_client.py`](../outputs/assignment_client.py): pool, claim, and
complete as reusable functions. Lesson 05's inbox builds on the same two queries.

## Check Yourself

**Q1.** Why is `flowable:assignee="ravi"` (a literal) a deployment risk?

- A) it's slower than groups
- B) instances created while it's deployed are pinned to Ravi personally — leave, transfer, or exit strands them
- C) Ravi gets too many emails
- D) literals aren't allowed

<details><summary>Answer</summary>B — the model outlives the org chart. Rules
(groups, expressions) age well; names don't.</details>

**Q2.** A claimed task no longer appears in `group_pool("credit-ops")` because…

- A) it was deleted
- B) the pool query filters `unassigned: true` — claiming set an assignee, moving it from the pool view to the person's list
- C) REST caches aggressively
- D) the group was removed

<details><summary>Answer</summary>B — pool and personal list are two filters over
the same task table. The claim transition moves rows between them.</details>

**Q3.** "The customer's own relationship manager reviews the file." Best modelling?

- A) `assignee="priya"` — she's the RM today
- B) `assignee="${relationshipManager}"` with the RM resolved into a variable at intake
- C) candidate group `rms`
- D) a service task that emails someone

<details><summary>Answer</summary>B — genuinely personal work is the assignee case,
but the *name* comes from data, not the model. C would let any RM claim it, which is
a different policy.</details>

**Challenge.** Extend the client with `reassign_orphans(from_user, to_group)`. Find
every task assigned to a departed user (`assignee=from_user`), unclaim each one back
to the pool, and print the audit line. That script is the standard "Ravi resigned"
runbook — write it before you need it.

## Related

- Next: [Identity management](../../03-identity-management/docs/en.md)
- Previous: [The task lifecycle](../../01-task-lifecycle/docs/en.md)
