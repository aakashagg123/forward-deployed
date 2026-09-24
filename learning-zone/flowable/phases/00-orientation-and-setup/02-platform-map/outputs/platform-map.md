---
name: platform-map
description: One-page map of Flowable's engines, artifacts, and which engine answers which question
kind: platform-map
phase: 00
lesson: 02
---

# Flowable platform map

## The router — which engine answers this question?

| Question | Engine | Artifact | Course phase |
| :-- | :-- | :-- | :-- |
| In what order do steps happen, who/what does each? | BPMN | `.bpmn20.xml` | 1–4, 7, 8 |
| What work is *available*, human picks order? | CMMN | `.cmmn` | 6 |
| Given these inputs, what's the answer? | DMN | `.dmn` | 5 |
| What outside event starts/continues work? | Event registry | `.event` + `.channel` | 7 |

## Cross-references (all by key, all independently versioned)

- BPMN → DMN: decision task (`decisionTableReferenceKey`)
- CMMN → BPMN: process task (`processRef`)
- BPMN → CMMN: case service task
- Event registry → BPMN/CMMN: event-registry start events & catches

## Shared machinery (learn once, applies to all)

- One relational DB; runtime vs history split (Phase 2 / 9.01)
- Job executor family: async, timers, dead letters (2.04, 9.03)
- Service/API idioms: Repository / Runtime / Task / History, Java + REST
- Deployment & versioning semantics (Phase 8)

## Lineage & editions

- Flowable is a 2016 fork of Activiti by its original authors. The BPMN engine's
  lineage goes back to 2010.
- **Open source**: all four engines plus REST — everything this course uses.
- **Flowable Work / Design**: commercial modelers, task/admin UIs, and
  orchestration conveniences on the same engines. Evaluate this layer for
  UI/velocity (Phase 10, lesson 05), not for engine capability.

## Modelling smells → wrong column

| Smell | Move to |
| :-- | :-- |
| business rules in script tasks / gateway constants | DMN |
| BPMN diagram that's mostly optional, order-free tasks | CMMN (but read 6.04 first) |
| hand-rolled Kafka consumer that starts processes | event registry |
| CMMN case that's really a fixed sequence | BPMN |
