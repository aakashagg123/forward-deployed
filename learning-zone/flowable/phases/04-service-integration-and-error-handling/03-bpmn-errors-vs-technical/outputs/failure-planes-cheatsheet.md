---
name: failure-planes-cheatsheet
description: Decision table + review checklist for BPMN errors vs technical errors
kind: cheat-sheet
phase: 04
lesson: 03
---

# Two failure planes — the cheat sheet

**The one question:** would retrying change the answer?
**No** → business outcome → `BpmnError` → route it in the diagram.
**Yes** → technical fault → plain exception → rollback / retry / dead letter.

## Decision table

| Failure | Plane | Handling |
| :-- | :-- | :-- |
| No bureau record for PAN | business | `BpmnError("NO_BUREAU_RECORD")` → boundary → manual pull |
| Bureau HTTP 503 / timeout | technical | async task, retries, dead-letter alert |
| KYC documents mismatch | business | `BpmnError("KYC_MISMATCH")` → re-submission path |
| Disbursal API rejects: account frozen | business | `BpmnError("ACCOUNT_FROZEN")` → ops review |
| Disbursal API 500 | technical | retries with idempotency key (Phase 2 cheat sheet) |
| Offer declined by customer | business | not an error at all — model it as a normal gateway/message path |
| NPE / bad config in a delegate | technical | fix the code; dead letter is the symptom |

## Delegate code review checklist

- [ ] Every business outcome is a named `BpmnError` code — never a generic exception.
- [ ] Error codes come from the documented catalogue (they are the process's API).
- [ ] No `catch (Exception e) { throw new BpmnError(...) }` — that laundering turns
      malfunctions into "outcomes" and silently disables retries.
- [ ] No swallowing: `catch` + log + return normal is a hidden failure plane.
- [ ] Technical exceptions carry context (which call, which correlation ID) for the
      dead-letter triage.

## Model review checklist

- [ ] Every `BpmnError` a delegate can throw has a catcher (boundary event or event
      subprocess) somewhere in scope.
- [ ] Catch-all error boundaries only as a last line, never instead of named codes.
- [ ] Escalation from exhausted retries → BPMN error is explicit where ops needs a
      manual fallback path.
- [ ] No timeout/5xx handling drawn as diagram paths — that's the job executor's
      plane.
