---
name: engine-fit-checklist
description: Diagnostic for "should this flow run on a process engine?" with alternatives
kind: decision-guide
phase: 00
lesson: 01
---

# Do you want a process engine? — the checklist

Score one point per yes:

- [ ] The flow waits on people, documents, or deadlines for days or longer.
- [ ] Humans and systems interleave (reviews between API calls).
- [ ] Deadlines/SLAs/expiries change behaviour (reminders, escalations, expiry).
- [ ] Audit/compliance will ask "what happened, when, under which rules?"
- [ ] The business changes the flow/policy more often than engineering deploys.
- [ ] "Where is case X stuck?" is a question someone asks weekly.

**5–6:** strong engine case. Start at Phase 1.
**3–4:** engine plausible. Prototype the hairiest flow first (Phase 0, lesson 03).
**0–2:** use the right lighter tool:

| Situation | Use instead |
| :-- | :-- |
| short, automated, stable flow | status column + queue + retries |
| engineer-only orchestration, no business-facing model | durable execution (Temporal-style) |
| autonomous services, no central "where is X?" requirement | event choreography |
| one team's UI wizard | application state, not workflow |

Red flags that someone is solving the wrong problem with an engine:
"we'll use it as our microservice orchestrator for everything" — it's for
*business* processes, not RPC. "The diagram will document our code" — if it
doesn't execute, it will lie (Principle 2). "We need it for scale" — engines buy
coordination, not throughput.
