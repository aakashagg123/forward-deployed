# Roadmap — Flowable from scratch

The single source of truth for phases and lessons. Status glyphs: ✅ done · 🚧 in
progress · ⬚ planned.

Legend: `Type` is **Build** (from-scratch implementation) or **Use** (real Flowable
engine) or **Concept** (no code — PM/architect lesson). `Ships` is the artifact saved
under the lesson's `outputs/`.

---

## Phase 0 — Orientation & setup `4 lessons` ✅

> What Flowable is, where it came from (the Activiti fork), where it sits in the
> landscape, and getting a local engine running.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [What is a process engine, and when do you want one](./phases/00-orientation-and-setup/01-when-do-you-want-an-engine/docs/en.md) ✅ | Concept | — | decision guide |
| 02 | [The Flowable platform map: BPMN, CMMN, DMN, event registry](./phases/00-orientation-and-setup/02-platform-map/docs/en.md) ✅ | Concept | — | platform map |
| 03 | [Run Flowable locally: Docker, REST API, first ping](./phases/00-orientation-and-setup/03-run-locally/docs/en.md) ✅ | Use | Python | client |
| 04 | [The landscape: Flowable vs Camunda 7/8 vs Temporal vs DIY](./phases/00-orientation-and-setup/04-landscape/docs/en.md) ✅ | Concept | — | comparison table |

## Phase 1 — BPMN & the token model `5 lessons` ✅

> The execution semantics under every BPMN diagram: tokens moving through a graph.
> Build a token engine by hand, then deploy real BPMN XML to Flowable.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Tokens & sequence flow: a process engine in 100 lines](./phases/01-bpmn-and-the-token-model/01-tokens-and-sequence-flow/docs/en.md) ✅ | Build | Python | module |
| 02 | [Gateways: exclusive, parallel, inclusive](./phases/01-bpmn-and-the-token-model/02-gateways/docs/en.md) ✅ | Build | Python | module |
| 03 | [BPMN 2.0 XML by hand](./phases/01-bpmn-and-the-token-model/03-bpmn-xml-by-hand/docs/en.md) ✅ | Build | XML | process model |
| 04 | [Use It: deploy & run on Flowable over REST](./phases/01-bpmn-and-the-token-model/04-run-it-on-flowable/docs/en.md) ✅ | Use | Python | client |
| 05 | [User tasks vs service tasks: where humans and systems meet](./phases/01-bpmn-and-the-token-model/05-human-and-service-tasks/docs/en.md) ✅ | Concept | — | decision guide |

## Phase 2 — The engine: state & transactions `5 lessons` ✅

> Why a process engine is really a state machine with a database: wait states,
> variables, transaction boundaries, and the job executor.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Wait states & persistence: why the engine sleeps](./phases/02-the-engine-state-and-transactions/01-wait-states-and-persistence/docs/en.md) ✅ | Build | Python | module |
| 02 | [Process variables & scope](./phases/02-the-engine-state-and-transactions/02-process-variables/docs/en.md) ✅ | Build | Python | module |
| 03 | [Transaction boundaries & async continuations](./phases/02-the-engine-state-and-transactions/03-transactions-and-async/docs/en.md) ✅ | Concept | — | cheat sheet |
| 04 | [The job executor: timers, retries, async work](./phases/02-the-engine-state-and-transactions/04-job-executor/docs/en.md) ✅ | Build | Python | module |
| 05 | [Use It: the embedded engine in Spring Boot](./phases/02-the-engine-state-and-transactions/05-embedded-engine-spring-boot/docs/en.md) ✅ | Use | Java | starter |

## Phase 3 — User tasks, identity & forms `5 lessons` ✅

> The human side: task lifecycle, assignment strategies, candidate groups,
> delegation, and forms.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [The task lifecycle: created → assigned → completed](./phases/03-user-tasks-identity-and-forms/01-task-lifecycle/docs/en.md) ✅ | Build | Python | module |
| 02 | [Assignment: assignee, candidate users, candidate groups](./phases/03-user-tasks-identity-and-forms/02-assignment/docs/en.md) ✅ | Use | Python | client |
| 03 | [Identity management: users, groups, and external IdPs](./phases/03-user-tasks-identity-and-forms/03-identity-management/docs/en.md) ✅ | Concept | — | decision guide |
| 04 | [Forms: form properties, form keys, external form apps](./phases/03-user-tasks-identity-and-forms/04-forms/docs/en.md) ✅ | Use | Python | client |
| 05 | [Task queries & the task inbox pattern](./phases/03-user-tasks-identity-and-forms/05-task-queries-and-inbox/docs/en.md) ✅ | Use | Python | client |

## Phase 4 — Service integration & error handling `6 lessons` ✅

> The system side: service tasks, delegates, HTTP tasks, BPMN errors vs technical
> errors, retries, and compensation.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Service tasks: delegates, expressions, delegate expressions](./phases/04-service-integration-and-error-handling/01-service-tasks-and-delegates/docs/en.md) ✅ | Use | Java | module |
| 02 | [The HTTP task: calling REST APIs from a process](./phases/04-service-integration-and-error-handling/02-http-task/docs/en.md) ✅ | Use | XML | process model |
| 03 | [BPMN errors vs technical errors: two failure planes](./phases/04-service-integration-and-error-handling/03-bpmn-errors-vs-technical/docs/en.md) ✅ | Concept | — | cheat sheet |
| 04 | [Boundary events: catching errors on an activity](./phases/04-service-integration-and-error-handling/04-boundary-events/docs/en.md) ✅ | Build | Python | module |
| 05 | [Retries & incident handling: what happens when a bureau call fails](./phases/04-service-integration-and-error-handling/05-retries-and-incidents/docs/en.md) ✅ | Use | Python | client |
| 06 | [Compensation: undoing completed work](./phases/04-service-integration-and-error-handling/06-compensation/docs/en.md) ✅ | Concept | — | pattern guide |

## Phase 5 — DMN: decisions as tables `4 lessons` ✅

> Externalise business rules into decision tables the business can read — and change
> without a deploy.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [A decision engine in 80 lines: rules, inputs, outputs](./phases/05-dmn-decisions/01-decision-engine-from-scratch/docs/en.md) ✅ | Build | Python | module |
| 02 | [Hit policies: FIRST, UNIQUE, COLLECT and why they matter](./phases/05-dmn-decisions/02-hit-policies/docs/en.md) ✅ | Build | Python | module |
| 03 | [DMN XML & the decision task: wiring DMN into BPMN](./phases/05-dmn-decisions/03-dmn-xml-and-decision-task/docs/en.md) ✅ | Use | XML | decision table |
| 04 | [Who owns the rules? Decision governance for product teams](./phases/05-dmn-decisions/04-decision-governance/docs/en.md) ✅ | Concept | — | decision guide |

## Phase 6 — CMMN: case management `4 lessons` ✅

> When work doesn't follow a fixed path: cases, stages, milestones, and sentries —
> and the honest answer on when you actually need CMMN.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Processes vs cases: prescribed flow vs available work](./phases/06-cmmn-case-management/01-processes-vs-cases/docs/en.md) ✅ | Concept | — | decision guide |
| 02 | [Plan items, stages, milestones, sentries](./phases/06-cmmn-case-management/02-plan-items-and-sentries/docs/en.md) ✅ | Use | XML | case model |
| 03 | [Mixing BPMN and CMMN: process tasks inside cases](./phases/06-cmmn-case-management/03-mixing-bpmn-and-cmmn/docs/en.md) ✅ | Use | XML | case model |
| 04 | [When CMMN is overkill (most of the time)](./phases/06-cmmn-case-management/04-when-cmmn-is-overkill/docs/en.md) ✅ | Concept | — | decision guide |

## Phase 7 — Events, timers & messaging `5 lessons` ✅

> Time and the outside world: timer events, signals, messages, and the event
> registry (Kafka, JMS, RabbitMQ).

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Timer events: ISO-8601 durations, cycles, due dates](./phases/07-events-timers-and-messaging/01-timer-events/docs/en.md) ✅ | Build | Python | module |
| 02 | [Message events: correlating the outside world to an instance](./phases/07-events-timers-and-messaging/02-message-events/docs/en.md) ✅ | Build | Python | module |
| 03 | [Signals vs messages: broadcast vs point-to-point](./phases/07-events-timers-and-messaging/03-signals-vs-messages/docs/en.md) ✅ | Concept | — | cheat sheet |
| 04 | [The event registry: Kafka in, process out](./phases/07-events-timers-and-messaging/04-event-registry/docs/en.md) ✅ | Use | Python | client |
| 05 | [Event subprocesses & interrupting vs non-interrupting starts](./phases/07-events-timers-and-messaging/05-event-subprocesses/docs/en.md) ✅ | Use | XML | process model |

## Phase 8 — Versioning & migration `4 lessons` ✅

> Long-running instances outlive their definitions. Version tags, running-instance
> migration, and deployment strategy.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Definition versions: what a redeploy actually does](./phases/08-versioning-and-migration/01-definition-versions/docs/en.md) ✅ | Use | Python | client |
| 02 | [Instance migration: moving live tokens to a new version](./phases/08-versioning-and-migration/02-instance-migration/docs/en.md) ✅ | Use | Python | client |
| 03 | [Blue-green for processes: strategies that survive audits](./phases/08-versioning-and-migration/03-blue-green-for-processes/docs/en.md) ✅ | Concept | — | pattern guide |
| 04 | [Backward-compatible model changes: a checklist](./phases/08-versioning-and-migration/04-compatibility-checklist/docs/en.md) ✅ | Concept | — | checklist |

## Phase 9 — Operations & observability `5 lessons` ✅

> Running it for real: history levels, the database, async executor tuning,
> metrics, and the admin surface.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [The history tables: audit trail vs runtime state](./phases/09-operations-and-observability/01-history-tables/docs/en.md) ✅ | Concept | — | cheat sheet |
| 02 | [History levels & data growth: the retention decision](./phases/09-operations-and-observability/02-history-levels/docs/en.md) ✅ | Concept | — | decision guide |
| 03 | [Async executor tuning: threads, acquisition, lock times](./phases/09-operations-and-observability/03-executor-tuning/docs/en.md) ✅ | Use | Java | settings |
| 04 | [Metrics & health: what to alert on](./phases/09-operations-and-observability/04-metrics-and-health/docs/en.md) ✅ | Use | Python | dashboard spec |
| 05 | [The database is the engine: sizing, indexes, cleanup jobs](./phases/09-operations-and-observability/05-database-runbook/docs/en.md) ✅ | Concept | — | runbook |

## Phase 10 — Architecture & product decisions `5 lessons` ✅

> The PM/architect capstone layer: embed vs standalone, multi-tenancy, build vs
> buy, and the honest competitive landscape.

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Embedded vs standalone vs Flowable Work: deployment topologies](./phases/10-architecture-and-product-decisions/01-deployment-topologies/docs/en.md) ✅ | Concept | — | decision guide |
| 02 | [Multi-tenancy: shared engine, shared tables, or neither](./phases/10-architecture-and-product-decisions/02-multi-tenancy/docs/en.md) ✅ | Concept | — | decision guide |
| 03 | [Where the process ends and the domain begins: anti-corruption](./phases/10-architecture-and-product-decisions/03-process-domain-boundary/docs/en.md) ✅ | Concept | — | pattern guide |
| 04 | [Build vs buy vs open source: the workflow TCO conversation](./phases/10-architecture-and-product-decisions/04-build-vs-buy/docs/en.md) ✅ | Concept | — | decision guide |
| 05 | [Flowable open source vs Flowable Work vs Camunda 8 vs Temporal](./phases/10-architecture-and-product-decisions/05-competitive-landscape/docs/en.md) ✅ | Concept | — | comparison table |

## Phase 11 — Capstone: loan origination `4 lessons` ✅

> One end-to-end build: BPMN flow + DMN credit decision + user-task review + bureau
> service calls + offer-expiry timers + error handling, driven over REST.

| # | Project | Combines | Lang | Ships |
|---|---------|----------|------|-------|
| 01 | [The process model: application → decision → offer → disbursal](./phases/11-capstone-loan-origination/01-process-model/docs/en.md) ✅ | 1, 4, 7 | XML | process model |
| 02 | [The credit decision table](./phases/11-capstone-loan-origination/02-credit-decision-table/docs/en.md) ✅ | 5 | XML | decision table |
| 03 | [The driver: a REST client that runs a full application](./phases/11-capstone-loan-origination/03-the-driver/docs/en.md) ✅ | 2, 3, 4 | Python | client |
| 04 | [Failure drill: bureau down, offer expired, manual override](./phases/11-capstone-loan-origination/04-failure-drill/docs/en.md) ✅ | 4, 7, 9 | Python | runbook |
