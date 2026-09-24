---
name: signal-message-cheatsheet
description: Decision table for choosing message vs signal events, with review flags
kind: cheat-sheet
phase: 07
lesson: 03
---

# Message or signal? — the cheat sheet

## The two questions

1. **Can you name the one instance this is for?** → key exists → **message**.
2. **Is zero receivers a normal outcome?** → yes → **signal**.

Disagreeing answers (a key exists AND zero receivers is fine) usually mean a
message. You must handle its "nobody waiting" case explicitly (park + alert).

## Decision table

| Event | Verdict |
| :-- | :-- |
| Bureau/e-sign/payment webhook for application X | message, key = application ID |
| Checker approves item X | message, key = item ID |
| Repo rate revised | signal |
| Compliance freeze on all onboarding | signal (event subprocess per model) |
| Customer withdraws application X | message (often an interrupting event subprocess) |
| Nightly cut-off reached | timer, not an event at all |
| New application arrives from channel | message/registry **start** event |

## Model-review flags

- ❌ Signal name containing an ID or expression (`paymentConfirmed-${orderId}`) —
  it's a message in costume; correlation safety is lost.
- ❌ Message delivery code that ignores "no subscription found" — unmatched
  deliveries get parked and alerted, never dropped.
- ❌ Signal caught by unbounded instance populations with synchronous heavy work
  after the catch — insert an async continuation (Phase 2) or the throw's
  transaction pays for every receiver.
- ❌ Message used where any number of receivers should react — you'll deliver to
  one arbitrary instance and strand the rest.
- ✅ Business key set at instance start (`businessKey = application ID`) — the
  precondition for webhook correlation queries.
