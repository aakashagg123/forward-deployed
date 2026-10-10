# Long-term memory

> **Motto** — Long-term memory is a store you write facts to and retrieve the relevant few from.

*Part of Phase 03 — Context and memory.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

The scratchpad dies with the session. A saved session belongs to one conversation. Some knowledge should outlive both: "this project uses pnpm", "the auth flow lives in `auth/`", "we decided against Redis".

A durable store solves this. The agent writes facts to it. On later tasks the harness retrieves the relevant ones.

The hard part is reading. If you load the whole store into every prompt, it grows until it crowds out the task. This is the same budget problem as in [Context budget](../../01-context-budget/docs/en.md). Retrieval keeps the prompt small as the store grows.

## The Concept

<style>
.dgm-ltm{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ltm-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-ltm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-ltm-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-ltm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-ltm-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-ltm-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-ltm-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-ltm-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-ltm-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-ltm-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-ltm-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-ltm{padding:20px 16px 18px}.dgm-ltm-row{flex-direction:column}}
</style>
<div class="dgm-ltm">
  <span class="dgm-ltm-chip">Write once, retrieve by relevance</span>
  <h4>remember() writes to a store; a new task retrieves the top-k relevant facts</h4>
  <p class="dgm-ltm-sub">Retrieval is scoped to what's relevant to the current query, not the whole store.</p>
  <div class="dgm-ltm-row">
    <div class="dgm-ltm-n accent">remember(fact)</div>
    <span class="dgm-ltm-arr">→</span>
    <div class="dgm-ltm-n blue">Memory store</div>
  </div>
  <div class="dgm-ltm-row" style="margin-top:8px">
    <div class="dgm-ltm-n neutral">New task / query</div>
    <span class="dgm-ltm-arr">→</span>
    <div class="dgm-ltm-n blue">Retrieve top-k relevant facts</div>
    <span class="dgm-ltm-arr">→</span>
    <div class="dgm-ltm-n green">Inject into context</div>
  </div>
</div>


Writing appends a fact. Reading ranks the facts by relevance and returns the top few. Only those few enter the context.

Three rules keep the store useful.

- **Write durable facts only.** Skip chat and one-off details. A fact should help a future task.
- **Deduplicate and forget.** A store full of repeats and stale claims gives bad answers.
- **Record the source.** A fact the agent copied from an untrusted page is a poisoning risk. Label retrieved facts as data when you inject them, as in [Assemble and inject](../../02-assemble-and-inject/docs/en.md).

This lesson ranks by word overlap with a rare-word bonus. Phase 08 shows how to retrieve over code: [Repo map](../../../08-extending-mcp-skills-retrieval/04-repo-map/docs/en.md).

## Build It

`code/long_term.py` stores facts in a JSON file. A new instance reads the same file, so facts survive the process.

```python
    def remember(self, fact, tags=(), source="agent"):
        if any(words(e["fact"]) == words(fact) for e in self.facts):
            return "duplicate"                       # same words, same fact
        self.facts.append({"fact": fact, "tags": list(tags), "source": source})
        self._save()
        return "remembered"
```

```python
    def retrieve(self, query, k=3):
        q = words(query)
        n = len(self.facts)

        def idf(w):                                  # rare words count more than common ones
            hits = sum(1 for e in self.facts if w in words(e["fact"]) | set(e["tags"]))
            return math.log(1 + n / hits) if hits else 0.0

        def score(e):
            return sum(idf(w) for w in q & (words(e["fact"]) | set(e["tags"])))

        ranked = sorted(self.facts, key=score, reverse=True)
        return [e["fact"] for e in ranked[:k] if score(e) > 0]
```

The `words` helper lowercases text and drops filler words and punctuation. The old version split on spaces, so "npm." never matched "npm". The `_save` method uses the same atomic write as the session store.

The asserts prove four things. A query returns the matching fact and nothing else. A query with no match returns an empty list. A second instance reads the facts the first one wrote. A repeated fact is ignored, and `forget` removes a stale one for good.

## Use It

Claude Code has two memory systems, and both load at the start of every session. `CLAUDE.md` holds instructions you write. Auto memory holds notes Claude writes for itself. It saves four kinds: `user`, `feedback`, `project` and `reference`. It skips anything it can derive from the code. The first 200 lines or 25KB of `MEMORY.md` load each session. Run `/memory` to toggle it.

In the API, the memory tool gives Claude a `/memories` directory. Add `{"type": "memory_20250818", "name": "memory"}` to `tools`. Claude then sends `view`, `create`, `str_replace`, `insert`, `delete` and `rename` requests. Your code runs them. Memory lives entirely in your application, so you pick the storage. Your handler must reject any path outside `/memories`, because a path like `/memories/../../secrets.env` is an attack.

`code/long_term_memory_sdk.py` uses the Python SDK helper `BetaLocalFilesystemMemoryTool`. It needs `pip install anthropic` and an API key, so it does not run offline.

## Challenge

Add an expiry rule. Give each fact a `last_used` time. Make `retrieve` update it, and make `forget_stale(days)` remove old facts. Assert that a fact used today survives and an old one goes.

## Sources

Claude Code docs, "How Claude remembers your project" (code.claude.com/docs/en/memory). Claude API docs, "Memory tool" (platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool).

Next: [System prompt and steering](../../../04-prompts-and-instructions/01-system-prompt-and-steering/docs/en.md)
