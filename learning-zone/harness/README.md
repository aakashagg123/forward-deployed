<div align="center">

# Harness engineering — from scratch

**Build a coding agent's harness by hand, one piece at a time. Then run the same piece
through the real tools.** 10 phases, 41 lessons.

![Phases](https://img.shields.io/badge/phases-10-d97757?style=flat-square&labelColor=181818)
![Track](https://img.shields.io/badge/track-build%20it%20%2F%20use%20it-d97757?style=flat-square&labelColor=181818)

**[🗺️ Roadmap](./ROADMAP.md)** · **[📐 Ten principles](./foundations/harness-principles.md)**

</div>

A *harness* is the system around the model: the loop, tools, context, memory,
permissions, subagents and evals. Here you build each piece yourself with the standard
library. Then each **Use It** section maps the piece to how Claude Code and the SDKs do it.

## How it works

Each lesson has five beats: **Motto → Problem → Concept → Build It → Use It.** Every code
file runs offline and ends with assertions, so a broken piece fails loudly. Each phase ends
with a short **Test yourself**.

## Start here

- **Find your level:** run `/find-your-level` for a short placement quiz. Or open the
  [Roadmap](./ROADMAP.md).
- **Read the spine first:** [The ten principles](./foundations/harness-principles.md).
- **First lesson:** [The agent loop](./phases/01-foundations-and-the-loop/03-the-agent-loop/docs/en.md).
- **The finish line:** [Capstone](./phases/10-capstone/01-assemble-the-agent/docs/en.md).

## Run the code

```bash
python3 harness-engineering/phases/01-foundations-and-the-loop/03-the-agent-loop/code/agent_loop.py
python3 harness-engineering/phases/10-capstone/01-assemble-the-agent/code/test_agent.py
```

## Connects to other tracks

You build the harness here. These tracks cover the same problems from other angles.

- [What is an agent?](../agentic-ai/what-is-an-agent.md) — the conceptual view of the loop.
- [Tool calling](../tool-calling/README.md) — tool contracts and MCP at product level.
- [Memory & context](../memory-and-context/README.md) — memory design behind phase 3.
- [Prompt engineering](../prompt-engineering/README.md) — prompt craft behind phase 4.
- [AI security & guardrails](../ai-security-and-guardrails/README.md) — the threat model behind phase 6.
- [Evaluation & observability](../evaluation-and-observability/README.md) — the eval case behind phase 9.
- [Cost optimization](../cost-optimization/README.md) — the cost layer above tracing.
- [Agentic workflows](../agentic-workflows/README.md) — orchestration patterns beyond phase 7.
- [RAG & vector databases](../rag-vector-databases/README.md) — retrieval beyond the repo map.
- [Running an agent in production](../ai-agents/running-an-agent-in-production.md) — limits, gates and the kill switch.

<div align="center"><sub>Educational content. Use it, fork it, teach from it.</sub></div>
