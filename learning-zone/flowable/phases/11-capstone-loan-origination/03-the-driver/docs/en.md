# Capstone 03 — The driver: a REST client that runs a full application

> **Motto** — If you can drive the whole journey from a hundred lines of stdlib
> Python, every UI, batch job, and integration after it is just a different caller.

*Part of Phase 11 — Capstone. Combines Phases 1, 2, 3, 4.*

## The Project

[`code/run_application.py`](../code/run_application.py) deploys both capstone
artifacts and walks one application end to end — deliberately using only helpers
built in earlier phases:

```
$ python3 run_application.py 720 400000 salaried
deployed loan-decision.dmn
deployed loan-origination.bpmn20.xml

started APP-3F91C2 (instance 12501): score=720 amount=400,000 salaried
  completing 'Pull bureau report manually' with {'score': 720}
  completing 'KYC document review' with {'kycOk': True}
  completing 'Accept loan offer' with {'accepted': True}

audit timeline: applicationReceived -> forkChecks -> bureauPull -> bureauDown
  -> manualBureauPull -> kycReview -> joinChecks -> kycGate -> decideCredit
  -> route -> acceptOffer -> acceptGate -> disburse -> doneDisbursed
decision=auto-approve rate=11.5 outcome=disbursed
```

What the run demonstrates, line by line:

- **`bureauDown -> manualBureauPull` is in every timeline on purpose.** The
  driver points `bureauBaseUrl` at `bureau.invalid`, so the Phase 4 error
  boundary fires deterministically. The design claim is that the failure path
  is *ordinary*: swap in a real URL and the same driver takes the happy branch
  with zero changes.
- **`open_tasks` polls briefly.** The bureau task is async (Phase 2), so
  between start and the boundary firing there's a moment with no open task and
  a live instance. The driver distinguishes "instance finished" from "instance
  thinking" — the same distinction your UI will need.
- **The work loop is inbox-shaped.** It fetches open tasks, answers by
  `taskDefinitionKey`, and repeats until none are left. It's Phase 3's inbox
  pattern with a dict where the human goes.
- **`businessKey=APP-…` from day one.** Nothing correlates on it *yet*, but the
  Phase 7 withdrawal message and the event-registry intake both need it.
  Retrofitting business keys onto live instances is miserable.

Three runs to try:

```bash
python3 run_application.py 780 800000 salaried        # row 1: rate 10.5, no review
python3 run_application.py 720 800000 self-employed   # falls to manual review
python3 run_application.py 600 100000 salaried        # declined at the route gateway
```

The second run parks at `creditReview`, and the driver answers it with approve.
Delete that line from `answers` and you have a live instance to point Phase 3's
`inbox_client.py` at instead.

**Challenge.** Add `--park` mode: complete only KYC, then print the inbox commands a
human would run to finish the application by hand (claim, form-data, complete). Then
run drill 3 from [lesson 04](../../04-failure-drill/docs/en.md) using
`offerValidity=PT15S`, and watch the timeline end in `expired` with nobody acting.
The engine keeps a promise no caller made it keep.
