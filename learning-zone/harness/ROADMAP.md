# Harness engineering from scratch — roadmap

> Build a coding agent's harness by hand, one piece at a time. Then run the same piece
> through the real tools. **10 phases, 41 lessons.** Every code file runs with the
> standard library and ends with assertions.

The phases stack. The model as a function is the floor. A working coding agent is the roof.
Skip a lower layer only if you already know it.

<style>
.dgm-rmap{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rmap-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-rmap h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-rmap-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-rmap-tier{margin-bottom:10px}
.dgm-rmap-tier-label{font-size:9px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;
  letter-spacing:.4px;margin-bottom:6px}
.dgm-rmap-row{display:flex;flex-wrap:wrap;gap:6px}
.dgm-rmap-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:7px 10px;
  font-size:10px;font-weight:700;color:var(--color-text)}
.dgm-rmap-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
@media (max-width:640px){.dgm-rmap{padding:20px 16px 18px}}
</style>
<div class="dgm-rmap">
  <span class="dgm-rmap-chip">The roadmap</span>
  <h4>Ten phases, five tiers</h4>
  <p class="dgm-rmap-sub">Skip ahead if you already know a lower tier. Do not skip and then wonder why a higher one breaks.</p>
  <div class="dgm-rmap-tier"><div class="dgm-rmap-tier-label">Tier 0 — the loop</div><div class="dgm-rmap-row"><div class="dgm-rmap-n accent">1 Foundations &amp; the loop</div></div></div>
  <div class="dgm-rmap-tier"><div class="dgm-rmap-tier-label">Tier 1 — what the loop acts through</div><div class="dgm-rmap-row"><div class="dgm-rmap-n accent">2 Tools</div></div></div>
  <div class="dgm-rmap-tier"><div class="dgm-rmap-tier-label">Tier 2 — built on tools</div><div class="dgm-rmap-row"><div class="dgm-rmap-n">3 Context &amp; memory</div><div class="dgm-rmap-n">4 Prompts &amp; instructions</div><div class="dgm-rmap-n">5 Files &amp; shell</div><div class="dgm-rmap-n">8 Extending: MCP, skills, retrieval</div></div></div>
  <div class="dgm-rmap-tier"><div class="dgm-rmap-tier-label">Tier 3 — control and coordination</div><div class="dgm-rmap-row"><div class="dgm-rmap-n">6 Permissions &amp; security</div><div class="dgm-rmap-n">7 Planning &amp; subagents</div></div></div>
  <div class="dgm-rmap-tier"><div class="dgm-rmap-tier-label">Tier 4 — ship it</div><div class="dgm-rmap-row"><div class="dgm-rmap-n accent">9 Reliability, evals &amp; ops</div><div class="dgm-rmap-n accent">10 Capstone</div></div></div>
</div>


## The phases

| # | Phase | Lessons | You build |
| --- | --- | --- | --- |
| 1 | [Foundations & the loop](./phases/01-foundations-and-the-loop/README.md) | 5 | A REPL, a prompt-cache layout, the agent loop, stop rules, a streaming loop |
| 2 | [Tools](./phases/02-tools/README.md) | 3 | A tool registry, validation and error results, parallel tool calls |
| 3 | [Context & memory](./phases/03-context-and-memory/README.md) | 5 | A token budget, message assembly, compaction, session resume, long-term memory |
| 4 | [Prompts & instructions](./phases/04-prompts-and-instructions/README.md) | 3 | A system prompt, memory files, an output contract |
| 5 | [Files & shell](./phases/05-files-and-shell/README.md) | 6 | Read, edit and search tools, a bash tool, background jobs, a sandbox and egress guard |
| 6 | [Permissions & security](./phases/06-permissions-and-security/README.md) | 4 | A permission gate, hooks, a settings file, defenses for untrusted content |
| 7 | [Planning & subagents](./phases/07-planning-and-subagents/README.md) | 4 | A todo list, plan mode, a sprint contract with waves, a supervisor and workers |
| 8 | [Extending: MCP, skills, retrieval](./phases/08-extending-mcp-skills-retrieval/README.md) | 5 | An MCP server and client, a skill, a repo map, a `search_code` tool |
| 9 | [Reliability, evals & ops](./phases/09-reliability-evals-and-ops/README.md) | 5 | A failure ladder, budgets, an eval gate, tracing and cost, a rollout switch |
| 10 | [Capstone](./phases/10-capstone/README.md) | 1 | One agent that combines the pieces and passes a real test |

## How to use this track

- Read [The ten principles](./foundations/harness-principles.md) first. They describe one
  multi-agent pattern. Phase 7 builds it.
- Each phase ends with a short **Test yourself**. The `/check-understanding` skill can quiz
  you on a phase. The `/find-your-level` skill picks a starting phase.
- Each lesson follows the same beats: Motto, Problem, Concept, Build It, Use It.

## What this track leaves to other tracks

Model internals, general RAG, the product case for evals, the security taxonomy and cost
strategy are covered elsewhere. Phases link to them where they matter.

| Topic | Read |
| --- | --- |
| Sampling, tokens, the context window | [LLMs](../llms/README.md) |
| Embeddings and hybrid search | [RAG & vector databases](../rag-vector-databases/README.md) |
| Evals and observability as a product decision | [Evaluation & observability](../evaluation-and-observability/README.md) |
| Attacks, red-teaming and compliance | [AI security & guardrails](../ai-security-and-guardrails/README.md) |
| Cost control | [Cost optimization](../cost-optimization/README.md) |
| Memory design | [Memory & context](../memory-and-context/README.md) |
