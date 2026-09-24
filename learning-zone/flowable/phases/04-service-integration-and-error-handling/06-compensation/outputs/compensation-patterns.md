---
name: compensation-patterns
description: Pattern card for BPMN compensation — XML skeleton, rules, decision checklist
kind: pattern-guide
phase: 04
lesson: 06
---

# Compensation — the pattern card

## The four rules

1. Only **completed** activities compensate.
2. Handlers run in **reverse** completion order.
3. Handlers are **ordinary tasks** — the retry/dead-letter pipeline applies to them.
4. Triggering is **explicit** — a compensation throw event you draw, never automatic.

## XML skeleton

```xml
<!-- the doer, with its undo pinned on -->
<serviceTask id="reserveFunds" flowable:delegateExpression="${treasuryReserve}"/>
<boundaryEvent id="reserveComp" attachedToRef="reserveFunds">
  <compensateEventDefinition/>
</boundaryEvent>
<serviceTask id="releaseFunds" isForCompensation="true"
    flowable:delegateExpression="${treasuryRelease}"/>
<association associationDirection="One"
    sourceRef="reserveComp" targetRef="releaseFunds"/>

<!-- somewhere later: the unwind trigger (e.g. on the withdrawal path) -->
<intermediateThrowEvent id="undoEverything">
  <compensateEventDefinition/>   <!-- no activityRef = compensate whole scope -->
</intermediateThrowEvent>
```

Notes: the handler is marked `isForCompensation="true"` (it is unreachable by normal
sequence flow) and linked by an `association`, not a `sequenceFlow`.

## Does this step need a handler? (checklist)

- [ ] Does the step commit an effect in an **external** system? (Engine-internal state
      needs no handler — rollback and normal flows cover it.)
- [ ] Can a **later** step abort the overall outcome? (If nothing after it can fail
      the whole, there is nothing to unwind for.)
- [ ] Is the undo **mechanical** — a cancel/release/void API with no approvals?
      (If the undo has its own workflow, model a subprocess on the failure path
      instead.)
- [ ] Is the undo **idempotent**? (Handlers retry; a double-release must be safe.)
- [ ] Could **reordering** remove the need? (Do the irreversible step last.)

Three or more boxes ticked → attach a handler. Otherwise simplify first.

## Testing minimum

- One test per prefix: fail after step 1, after step 2, … and assert exactly the
  right handlers ran, in reverse order.
- One test where a **handler** fails → assert it dead-letters and the incident is
  visible (lesson 05's triage finds it).
