# Run Flowable locally: Docker, REST API, first ping

> **Motto** — One container, one base URL, one credential pair. Everything this
> course does to a real engine starts from the three lines on this page.

*Part of Phase 00 — Orientation & setup. This is the phase's **Use It** lesson.*

## The Problem

Every Use It beat from Phase 1 onward assumes a running engine. Every "the lesson
doesn't work" report traces to one of three boring causes: the container isn't
running, the URL is wrong, or auth failed. This lesson pins the setup once and
ships a diagnostic that separates those causes in five seconds. It's the same
first-contact ritual you'll run against a *real* environment someday, where "is
it up, what's deployed, is anything stuck" are the opening moves of every
incident.

## The Concept

The course's standard environment:

```bash
docker run -p 8080:8080 flowable/flowable-rest
# REST base : http://localhost:8080/flowable-rest/service
# credentials: rest-admin / test
```

What that container is — and importantly, isn't:

| Property | Value | Consequence |
| :-- | :-- | :-- |
| Engines | all four (BPMN/CMMN/DMN/event registry) + REST | every lesson's Use It works against it |
| Database | in-container H2 by default | **state dies with the container** — a feature for lessons, never production |
| Auth | HTTP Basic, one admin user | fine locally; a real deployment puts your API layer in front (Phase 3, lesson 03) |
| Custom Java | none — you can't add delegates | why course models use expressions/HTTP/DMN tasks (Phases 1, 4, 5) |

Two upgrades exist, and this course defers both deliberately. Pointing the
container at PostgreSQL (`FLOWABLE_DATASOURCE_*` env vars) makes state survive
container replacement — Phase 2 lesson 01's Use It uses exactly that property.
The *embedded* topology (engine inside your Spring Boot app) is Phase 2 lesson 05
and the Phase 10 topology decision.

The REST surface follows one idiom everywhere, which is why a single ping script
generalises: `repository/*` for deployed artifacts, `runtime/*` for live state,
`management/*` for jobs and engine internals, `history/*` for the past, and
`query/*` for rich filters. Learn these five prefixes and you can navigate any
endpoint you haven't met yet.

## Use It

[`code/ping.py`](../code/ping.py) runs first contact — reachability, auth,
deployments, live state — with each failure mode named:

```
$ python3 ping.py
engine  : default 7.0.x
deployed: 0 process definition(s)
open instances : 0
open tasks     : 0
dead letters   : 0

engine is ready — next: deploy something (Phase 1, lesson 04's flowable_client.py)
```

The zeros on a fresh container are the correct answer. The same script, run
mid-course, doubles as a tiny health check — it's the ancestor of Phase 9's probe,
same queries, no thresholds. Kill the container and run the script again to see
the unreachable branch. Change the password to see the auth branch. Now you've
seen all three failure modes on purpose, before any lesson shows you one by
accident.

## Ship It

This lesson ships [`code/ping.py`](../code/ping.py) — first-contact diagnostics
you can run against any Flowable engine, local or remote.

## Check Yourself

**Q1.** You restart the default container and Phase 1's deployed model is gone.
This is…

- A) a bug
- B) the in-container H2 doing exactly what it does — state died with the container; use the PostgreSQL env vars when you want survival
- C) a licensing limit
- D) REST caching

<details><summary>Answer</summary>B — ephemerality is the trade you make with the
default setup. Phase 2's persistence promise applies to the *database*, and this
container's database lives inside it.</details>

**Q2.** A colleague's script gets HTTP 401 against the container. The fix is…

- A) restart Docker
- B) credentials — the image speaks Basic auth as rest-admin/test; 401 means reachable-but-unauthenticated, a different failure from unreachable
- C) use port 8081
- D) disable auth

<details><summary>Answer</summary>B — ping.py names the two branches separately.
Mixing them up wastes the first twenty minutes of every setup session.</details>

**Q3.** Which REST prefix answers "what *could* run" vs "what *is* running"?

- A) runtime vs history
- B) repository vs runtime
- C) management vs query
- D) form vs task

<details><summary>Answer</summary>B — repository holds deployed definitions, the
potential. Runtime holds live instances, the actual. The other prefixes follow
the same one-word logic.</details>

**Challenge.** Point the container at a local PostgreSQL (the official image docs
list the `FLOWABLE_DATASOURCE_*` variables), deploy Phase 1's model, destroy and
recreate the container, and run ping.py. Watch the deployment count survive —
that's Phase 2, lesson 01's claim, verified with your own hands on day zero.

## Related

- Next: [The landscape](../../04-landscape/docs/en.md)
- First real deployment: [Phase 1, lesson 04](../../../01-bpmn-and-the-token-model/04-run-it-on-flowable/docs/en.md)
