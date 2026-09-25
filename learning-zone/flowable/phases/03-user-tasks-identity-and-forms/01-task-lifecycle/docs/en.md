# The task lifecycle: created → assigned → completed

> **Motto** — A user task is a state machine with sharp edges. Claim makes one
> person accountable, and every refused transition is a double payment that
> didn't happen.

*Part of Phase 03 — User tasks, identity & forms.*

## The Problem

Phase 1 treated a user task as a token that sleeps until someone completes it. Put
five credit analysts in front of fifty applications, and "someone" becomes a problem.
Two analysts open the same case, and both spend twenty minutes on it. One submits, and
the other's work is lost — or, worse, both submit and the second overwrites the first.
Inboxes need an ownership protocol, and the engine must enforce it, not team etiquette.

## The Concept

<style>
.dgm-tl{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-tl-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-tl h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-tl-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-tl-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-tl-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-tl-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-tl-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-tl-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-tl-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-tl-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-tl-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-tl{padding:20px 16px 18px}.dgm-tl-row{flex-direction:column}}
.dgm-tl-note{margin-top:10px;padding:9px 14px;background:#faeceb;border:1px dashed #e3b3ad;border-radius:10px;
  font-size:10.5px;color:#7a2c2e;line-height:1.4}
</style>
<div class="dgm-tl">
  <span class="dgm-tl-chip">Task lifecycle</span>
  <h4>A task moves through four states — but not always forward</h4>
  <p class="dgm-tl-sub">Claim, delegate and unclaim are all reversible; complete is the only one-way door.</p>
  <div class="dgm-tl-row">
    <div class="dgm-tl-n blue">CREATED</div>
    <span class="dgm-tl-arr"><span class='lbl'>claim — one wins, everyone else refused</span>→</span>
    <div class="dgm-tl-n accent">CLAIMED</div>
    <span class="dgm-tl-arr"><span class='lbl'>complete (assignee only)</span>→</span>
    <div class="dgm-tl-n green">COMPLETED</div>
  </div>
  <div class="dgm-tl-note">CLAIMED can also move to DELEGATED (delegate → helper) and back (resolve), or return to CREATED (unclaim, back to the pool).</div>
</div>


The rules that carry the weight:

1. **CREATED is a pool, CLAIMED is a person.** An unclaimed task is visible to every
   candidate. Claim is an atomic race, and exactly one candidate wins. In Flowable
   that's an optimistic-locked update — the same job Phase 2's revision column does.
2. **Only the assignee completes.** Not "anyone in the group" — only the person who
   claimed the task. Between claim and complete, the engine refuses everyone else's
   claim attempts and gives a reason.
3. **Delegation preserves accountability.** Delegate hands the *work* to a helper but
   records the original assignee as `owner`. Resolve hands the work back. The audit
   trail shows both steps, which is what a maker-checker policy requires.
4. **Every transition is logged.** The log shows who claimed the task, when, and who
   delegated to whom. An ops dispute or an audit needs this evidence, and it exists
   because the lifecycle is explicit, not a single `status` column three services
   write to.

## Build It

[`code/task_lifecycle.py`](../code/task_lifecycle.py) — the machine is a dataclass
with five methods, and each method opens with its precondition:

```python
def claim(self, user, groups):
    self._check(self.state == "CREATED", f"cannot claim in state {self.state}"
                + (f" (held by {self.assignee})" if self.assignee else ""))
    self._check(self.visible_to(user, groups),
                f"{user} is not a candidate ({self.candidate_groups})")
    self.assignee, self.state = user, "CLAIMED"
```

The demo stages the claim race and the delegation round-trip:

```
$ python3 task_lifecycle.py
refused : Manual credit review: cannot claim in state CLAIMED (held by asha)
refused : Manual credit review: cannot claim in state CLAIMED (held by asha)
refused : Manual credit review: ravi is not the assignee

audit trail:
  - claimed by asha
  - asha delegated to meera
  - resolved by meera; back with asha
  - completed by asha
```

The refusals protect something concrete, not abstract data integrity. They save
twenty minutes of a second analyst's attention, and they prevent the ambiguity of two
submitted decisions.

## Use It

The same transitions over Flowable's task API — one call each:

```java
taskService.claim(taskId, "asha");          // TransitionError -> FlowableTaskAlreadyClaimedException
taskService.unclaim(taskId);
taskService.delegateTask(taskId, "meera");  // owner=asha, assignee=meera
taskService.resolveTask(taskId);            // back to asha, DelegationState.RESOLVED
taskService.complete(taskId, variables);
```

Over REST, one task endpoint handles all of this through an `action` field:
`{"action": "claim", "assignee": "asha"}`, `{"action": "delegate", ...}`,
`{"action": "resolve"}`, `{"action": "complete", "variables": [...]}`. The next
lesson's client drives these calls end to end.

## Ship It

This lesson ships [`code/task_lifecycle.py`](../code/task_lifecycle.py), the
lifecycle as an executable reference. It includes the refusal messages a good task
API owes its users.

## Check Yourself

**Q1.** Two analysts click "claim" on the same task within a millisecond. The engine
guarantees…

- A) both get it; last completer wins
- B) exactly one claim succeeds; the other receives an already-claimed error
- C) the task duplicates
- D) whoever has more permissions wins

<details><summary>Answer</summary>B — claim is an atomic, optimistic-locked
transition. The refused analyst lost a click, not twenty minutes of work.</details>

**Q2.** Asha delegates her review to Meera. Who completes the task, and what does
resolve do?

- A) Meera completes it directly
- B) Meera resolves it back to Asha, who completes — delegation lends the work, not the accountability
- C) either may complete
- D) the task returns to the group pool

<details><summary>Answer</summary>B — owner/assignee split exists precisely so the
sign-off stays with the person your policy holds accountable.</details>

**Q3.** Why does completing an unclaimed group task get refused?

- A) performance
- B) with no assignee there is no accountable person — the audit trail would say a group decided
- C) it isn't refused
- D) variables can't be written without an assignee

<details><summary>Answer</summary>B — claim-before-complete is the accountability
protocol. Flowable technically allows assignee-less completion through the API, but
teams that care about audits lock this down.</details>

**Challenge.** Add `escalate(to_group)`. A claimed task past its due date returns to
a *different* pool (the supervisors'), recording the original assignee. Then decide —
and defend — whether escalation should be allowed from DELEGATED, and what happens to
the owner field if so. You've just designed the policy questions that Phase 7's
escalation timers will trigger.

## Related

- Next: [Assignment: assignee, candidate users, candidate groups](../../02-assignment/docs/en.md)
- The wait state underneath: [Phase 1, lesson 01](../../../01-bpmn-and-the-token-model/01-tokens-and-sequence-flow/docs/en.md)
