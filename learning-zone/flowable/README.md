<div align="center">

# Flowable — from scratch

**Understand process automation by building a tiny process engine by hand. Then run the
same processes on the real Flowable engine.** Concept-first for PMs and architects, with a
technical build layer for engineers.

![Phases](https://img.shields.io/badge/phases-12-d97757?style=flat-square&labelColor=181818)
![Track](https://img.shields.io/badge/track-build%20it%20%2F%20use%20it-d97757?style=flat-square&labelColor=181818)

**[🗺️ Roadmap](./ROADMAP.md)** · **[📐 Ten Principles](./foundations/process-automation-principles.md)**

</div>

> This is a **separate track** from the Harness Engineering module. *Flowable* is an
> open-source business process automation platform — a 2016 fork of Activiti. It has four
> engines: BPMN 2.0 for structured processes, CMMN for case management, DMN for
> decisions, and an event registry for event-driven flows. Banks and fintechs run loan
> origination, KYC, and approval workflows on it. Here you learn the *execution model*
> underneath — tokens, wait states, transactions, jobs. You build it yourself, so the
> real engine is transparent when you use it.

## Audience — two layers, one track

- **PM / architect layer:** the `foundations/` spine and every **Concept** beat explain
  *when* and *why* to use BPMN, CMMN, or DMN, and when to embed the engine or run it
  standalone. They also compare Flowable, Camunda, and Temporal. No code is required.
- **Engineer layer:** every **Build It** implements the idea from scratch, in Python
  standard library, at about 80–150 lines. Every **Use It** runs the same thing on a real
  Flowable engine, over Docker and REST, or embedded in Spring Boot.

Read only the Concept beats and you get a complete architecture course. Do the builds
and you can reason about the engine's behaviour from first principles.

## How it works

Each lesson runs the same six beats: **Motto → Problem → Concept → Build It → Use It →
Ship It**, then a short self-quiz.

## Start here

- **Read the spine first:** [The ten principles of process automation](./foundations/process-automation-principles.md).
- **First worked lessons:**
  - [Tokens & sequence flow: a process engine in 100 lines](./phases/01-bpmn-and-the-token-model/01-tokens-and-sequence-flow/docs/en.md)
  - [Wait states & persistence: why the engine sleeps](./phases/02-the-engine-state-and-transactions/01-wait-states-and-persistence/docs/en.md)

## Status

**All 12 phases are complete** — orientation, BPMN & the token model, the engine's
state & transactions, user tasks & identity, service integration & error handling,
DMN decisions, CMMN case management, events & timers, versioning & migration,
operations & observability, architecture & product decisions, and the end-to-end
loan-origination capstone. Full lesson index: the [Roadmap](./ROADMAP.md).

## Run the code

```bash
python3 flowable/phases/01-bpmn-and-the-token-model/01-tokens-and-sequence-flow/code/token_engine.py
```

To run the **Use It** beats you need a local Flowable instance:

```bash
docker run -p 8080:8080 flowable/flowable-rest
# REST API at http://localhost:8080/flowable-rest/service, default user rest-admin/test
```

## Connects to other tracks

A process engine is infrastructure. These tracks frame the same decisions and failure modes.

- [Prioritization & roadmaps](../technical-product-management/prioritization-and-roadmaps.md) — the build-vs-buy judgment behind "do you even want an engine?" (Phase 0).
- [Reliability & failure](../technical-product-sense/reliability-and-failure.md) — the frame for wait states, transactions, and the job executor (Phase 2).
- [Function calling, tool contracts, idempotency](../content/02-reliable-outputs/function-calling.md) — the same idempotency and retry discipline as service tasks and boundary events (Phase 4).
- [Governance, quality & trust](../knowledge-graphs/governance-quality-and-trust.md) — decisions-as-data governance mirrors DMN decision governance (Phase 5).
- [Launches, rollouts & migrations](../technical-product-management/launches-rollouts-and-migrations.md) — the operating discipline behind process versioning & migration (Phase 8).
- [Technical product management for AI](../technical-product-management/tpm-for-ai-products.md) — "model upgrades as migrations," made concrete by Phase 8's instance-migration mechanics.
- [Multi-agent systems & protocols](../agentic-ai/multi-agent-and-protocols.md) — orchestration by a shared engine vs. by autonomous agents.
- [The method: deconstruct, challenge, reconstruct](../first-principles/the-method.md) — decomposing a workflow into tokens is first-principles thinking applied.

<div align="center"><sub>Educational content. Use it, fork it, teach from it.</sub></div>
