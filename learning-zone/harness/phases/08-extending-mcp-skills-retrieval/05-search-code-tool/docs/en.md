# A search_code Tool

> **Motto** — Wrap chunk, index and rank into one `search_code` tool that returns `path:line` hits the agent can act on.

*Part of Phase 08 — Extending: MCP, Skills, Retrieval.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

You have a repo map and structural chunks. The agent still needs one call it can make: "find the code that does X." Without it, the agent guesses names, runs `grep`, and reads whole files.

A **retrieval tool** answers that call. `search_code(query)` returns a short ranked list of locations. The agent then reads those locations and edits them. The tool does not return the code itself. It returns pointers, so the answer stays small.

## The Concept

<style>
.dgm-rt2{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rt2-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-rt2 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-rt2-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-rt2-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-rt2-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-rt2-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-rt2-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-rt2-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-rt2-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-rt2-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-rt2-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-rt2{padding:20px 16px 18px}.dgm-rt2-row{flex-direction:column}}
</style>
<div class="dgm-rt2">
  <span class="dgm-rt2-chip">Build the index once, search it every task</span>
  <h4>search_code(query) is the one tool an agent task actually calls</h4>
  <p class="dgm-rt2-sub">Top hits come back as path:line name. The agent still has to read and edit from there.</p>
  <div class="dgm-rt2-row">
    <div class="dgm-rt2-n neutral">Index: chunk and score (build once)</div>
  </div>
  <div class="dgm-rt2-row" style="margin-top:8px">
    <div class="dgm-rt2-n neutral">Agent task</div>
    <span class="dgm-rt2-arr">→</span>
    <div class="dgm-rt2-n accent">search_code(query)</div>
    <span class="dgm-rt2-arr">→</span>
    <div class="dgm-rt2-n green">Top hits: path:line name → read → edit</div>
  </div>
</div>


Build the index once. Search it on every task. A hit is `path:line  name`. The agent opens that line with the read tool.

A good retrieval tool also knows when it has nothing. A query with no match must return an empty answer. A tool that always returns its "closest" chunk sends the agent to the wrong file with full confidence.

## Build It

`code/retrieval_tool.py` is one stdlib file. It cuts each Python file into one chunk per top-level definition, with decorators included. The scorer is TF-IDF: a word that appears in few chunks counts for more than a word that appears everywhere. This is a lexical scorer. It matches shared words and does not understand meaning. A real embedding model would, and the next section says where it plugs in.

The tokenizer splits `loginUser` and `login_user` into `login` and `user`, so a query in prose can match an identifier:

```python
def tokens(text):
    """Lowercase words. Split snake_case and camelCase so `loginUser` matches `login`."""
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return [w for w in re.findall(r"[A-Za-z]+", spaced.lower()) if len(w) > 2]
```

The search method scores each chunk and drops chunks with no shared word:

```python
            if score > 0:                              # no shared word, no hit
                scored.append((score, f"{ch['path']}:{ch['line']}  {ch['name']}"))
```

`TOOL_SPEC` and `tool_call` wrap the search as a tool in the shape from [lesson 01](../../01-mcp-protocol-server-client/docs/en.md): an `inputSchema`, and a result with `content` and `isError`. An empty query returns `isError: true`. A query with no match returns a normal `no matches` result, because the tool worked and found nothing.

The asserts index a temp directory that holds a file with a syntax error. They check that the broken file is skipped, that prose finds the right function, that `loginUser` splits, that a decorated class reports its decorator line, and that an unrelated query returns nothing.

## Use It

`code/search_server_sdk.py` serves the same tool through the official SDK from [lesson 02](../../02-official-mcp-sdk/docs/en.md). It needs `pip install mcp`. I ran its `--check` mode against `mcp` 2.2.0 with an in-memory client. Register it with Claude Code:

```bash
claude mcp add --env REPO_ROOT=. code-search -- python3 code/search_server_sdk.py
```

Return hits, not files. Claude Code warns when an MCP tool returns more than 10,000 tokens, and its default maximum is 25,000 (`MAX_MCP_OUTPUT_TOKENS` changes it). A list of ten `path:line` strings is far below that.

To get semantic search, swap the scorer for an embedding model and keep the same tool shape. Claude Code already has `Glob` and `Grep` for exact matches, so a retrieval tool pays off when the question is about meaning and you do not know the names.

## Challenge

Make the index incremental. Add `update_file(path, source)` that removes a file's old chunks and adds the new ones, and keep `df` correct. Assert that after you rewrite `auth.py` with a new function name, a search finds the new name and no longer finds the old one.

## Sources

Claude Code docs, "Connect to tools via MCP" (code.claude.com/docs).

Next: [Failure ladder](../../../09-reliability-evals-and-ops/01-failure-ladder/docs/en.md)
