# Metrics & health: what to alert on

> **Motto** — Alert on work that *stays*: rows leaving the engine are success — old
> instances, deep pools, due jobs, and dead letters are the four shapes of stuck.

*Part of Phase 09 — Operations & observability.*

## The Problem

CPU, memory, and request latency all look fine on the platform team's dashboards.
Meanwhile two hundred applications sit dead-lettered (capstone drill 5), a pool
nobody staffs grows past 300, and one instance from March quietly holds a treasury
reservation. Process engines fail *by accumulation*, not by crashing, and
infrastructure metrics can't see accumulation.

The engine's own tables can. Every "is origination healthy?" question is a count
over runtime tables (lesson 01's routing rule). The whole monitoring problem is
choosing which counts, with which thresholds, wake which owner.

## The Concept

Six signals cover the failure modes this course has met, each pointing at its
earlier lesson:

| Signal | Detects | Threshold logic | Wakes |
| :-- | :-- | :-- | :-- |
| **dead-letter count** | silent stuck async work (Phase 4.05) | **> 0** — normal is zero, full stop | on-call eng |
| **overdue timer jobs** | executor not keeping up (9.03) | small buffer over acquisition lag | on-call eng |
| **oldest open instance** | zombie instances holding real-world state | multiple of the process's *designed* lifetime | process owner |
| **deepest pool + age** | staffing vs inflow (Phase 3.05) | per-team SLA on queue depth/oldest item | ops lead |
| **overdue tasks** | SLA breaches in progress (dueDate, Phase 3/7) | your SLA minus reaction time | ops lead |
| **throughput vs baseline** | upstream died / intake broke (from history) | rate drop > X% week-over-week | product owner |

Design rules that make these six work:

1. **Every alert names the human who can act.** Dead letters page engineering.
   Deep pools page the ops lead. A table bug pages the table's owner (Phase 5's
   governance). An alert routed to "the channel" is just a log line with anxiety.
2. **Thresholds derive from the process, not the infrastructure.** "Oldest
   instance > 45 days" means something *because* the capstone's offer expires at
   30 — the model's own timers define normal. Set thresholds per definition, not
   per engine.
3. **Poll the counts, not the rows.** Every signal is a `total` over an indexed
   query — cheap at any scale. The moment you page through rows for monitoring,
   you're building lesson 01's dashboards on the wrong endpoint.
4. **The probe is the contract; the transport is fashion.** The same six numbers
   feed a cron mail, a Prometheus exporter, or Flowable's actuator/micrometer
   metrics. Start with the numbers, and promote the transport when the team
   standardises.

## Use It

[`code/health_probe.py`](../code/health_probe.py) emits all six with thresholds and
a CI-friendly exit code:

```
$ python3 health_probe.py
open instances        : 143
dead-letter jobs      : 2
overdue timer jobs    : 0
oldest instance (days): 12.4
pools                 : {'credit-ops': 31, 'kyc-ops': 4, 'applicants': 9}
overdue tasks         : 7
ALERT dead_letter_jobs = 2 (threshold 0)
$ echo $?
1
```

Wire it as a cron job every 5 minutes: a non-zero exit posts the output to the
incident channel. That's a complete v1 monitoring stack — the capstone runbook's
five-line health check, made permanent. The dashboard spec
([`outputs/dashboard-spec.md`](../outputs/dashboard-spec.md)) defines the panel
layout and the history-side additions (cycle time, step durations) for the
eventual Grafana build.

## Ship It

This lesson ships both halves:
[`code/health_probe.py`](../code/health_probe.py) (the numbers, runnable today) and
[`outputs/dashboard-spec.md`](../outputs/dashboard-spec.md) (the dashboard those
numbers grow into).

## Check Yourself

**Q1.** Why is the dead-letter threshold exactly zero?

- A) storage cost
- B) each row is a frozen process invisible everywhere else — there is no "acceptable" number of silently stuck customer cases
- C) the API can't count higher
- D) it should be 10

<details><summary>Answer</summary>B — Phase 4's drill 5. One dead letter is one
customer whose case stopped moving with no human aware.</details>

**Q2.** "Oldest open instance" thresholds should come from…

- A) a standard 30 days
- B) the process's own designed lifetime — offer validity, SLA chain, timer horizons in the model
- C) database size
- D) gut feel per quarter

<details><summary>Answer</summary>B — the model defines normal duration; monitoring
just checks reality against the model's promise.</details>

**Q3.** Throughput dropped 60% but every runtime signal is green. Most likely…

- A) the engine is broken
- B) intake died upstream — nothing is *entering*; runtime signals only see work that arrived (that's why the sixth signal reads history rates)
- C) the probe is wrong
- D) normal variance

<details><summary>Answer</summary>B — accumulation metrics can't see absence.
Rate-vs-baseline is the one signal that watches the front door.</details>

**Challenge.** Add the history side to the probe: median time-to-decision over the
trailing 7 days (lesson 01's challenge computed it once), and week-over-week
application rate. Then run the capstone driver in a loop, kill your fake bureau
mid-run, and verify which signals fire in which order. The ordering *is* your
incident playbook.

## Related

- Next: [The database is the engine](../../05-database-runbook/docs/en.md)
- The stuck states being counted: [Phase 4, lesson 05](../../../04-service-integration-and-error-handling/05-retries-and-incidents/docs/en.md)
