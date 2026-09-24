<div align="center">

# Harness engineering — from scratch

**Build a production coding agent (a "harness" like Claude Code) by hand, one piece at a
time — then use the real SDKs.** Every lesson ships a reusable artifact.

![Phases](https://img.shields.io/badge/phases-20-d97757?style=flat-square&labelColor=181818)
![Track](https://img.shields.io/badge/track-build%20it%20%2F%20use%20it-d97757?style=flat-square&labelColor=181818)

**[🗺️ Roadmap](./ROADMAP.md)** · **[📐 Ten Principles](./foundations/harness-principles.md)**

</div>

> This is a **separate track** from the AI Engineering module (which lives in the repo
> root). A *harness* is the system around the model — the loop, tools, context, memory,
> permissions, subagents, and evals. Here you build each piece yourself, then run the
> same thing through the real framework, so the abstraction is transparent.

## Audience

This track assumes you work inside **Claude Code or Codex**. You build each piece of a
harness yourself to understand it. Every **Use It** section then maps that piece to how
those tools do it — memory files, hooks, skills, subagents, MCP, permissions. Every
shipped artifact installs directly into them.

## How it works

Each lesson runs the same six beats: **Motto → Problem → Concept → Build It → Use It →
Ship It**, then a short self-quiz. You implement from the standard library first, then
use the production SDK.

## Start here

- **Find your level:** run `/find-your-level` (placement quiz) — or just open the
  [Roadmap](./ROADMAP.md).
- **Read the spine first:** [The Ten Principles of a Working Harness](./foundations/harness-principles.md).
- **First worked lessons:**
  - [The agent loop from scratch](./phases/02-the-agent-loop/01-agent-loop/docs/en.md)
  - [Sprint contracts & budgeted waves](./phases/10-subagents-and-orchestration/01-sprint-contract-and-waves/docs/en.md)

## Status

All 20 phases are complete — see the [Roadmap](./ROADMAP.md) for the full phase-by-phase
breakdown. Quiz yourself per phase with `/check-understanding <phase>`.

## Run the code

```bash
python3 harness-engineering/phases/02-the-agent-loop/01-agent-loop/code/agent_loop.py
```

## Connects to other tracks

You build the harness here. These tracks frame the same problems from other altitudes.

- [What is an agent?](../agentic-ai/what-is-an-agent.md) — the conceptual view of the loop you build by hand in Phase 2.
- [Tool calling](../tool-calling/README.md) — the product-decision altitude of Phase 3's tool contracts and Phase 12's MCP integrations.
- [Context engineering](../content/00-foundations/context-engineering.md) — the discipline behind Phases 4 & 9 (context and memory).
- [RAG architecture](../content/03-rag/rag-architecture.md) — the retrieval stack under Phase 13's codebase understanding.
- [Multi-tenant isolation](../content/05-safety-multitenancy/multi-tenant-isolation.md) — the platform-layer version of Phase 17's tenant safety.
- [AI security & guardrails](../ai-security-and-guardrails/README.md) — the threat taxonomy and compliance layer above Phase 8's permission gating and Phase 17's security work.
- [Evals: golden sets, adversarial, LLM-as-judge](../content/04-evals-observability/evals.md) — the eval stack behind Phase 15's harness tests.
- [Evaluation & observability](../evaluation-and-observability/README.md) — the product-leader case for the eval investment Phase 15 and 16 build by hand.
- [Cost optimization](../cost-optimization/README.md) — the product-decision layer above Phase 16's cost tracking.
- [Reliability & failure](../technical-product-sense/reliability-and-failure.md) — the PM-altitude frame for Phase 14's failure modes.
- [The method: deconstruct, challenge, reconstruct](../first-principles/the-method.md) — the reasoning move behind building an engine from scratch.

<div align="center"><sub>Educational content. Use it, fork it, teach from it.</sub></div>
