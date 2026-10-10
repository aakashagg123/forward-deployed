# Phase 08 — Extending: MCP, Skills, Retrieval
*Part of [Harness engineering](../../README.md).*

A harness reaches beyond its built-in tools in three ways. MCP connects outside tool servers. Skills add workflows that load only when needed. Retrieval finds the right code in a large repo. This phase builds the MCP handshake by hand, then uses the official SDK. It then adds a skill index with deferred loading, a repo map, and a `search_code` tool.

## Lessons

1. [The MCP Protocol: Server and Client](./01-mcp-protocol-server-client/docs/en.md) — handshake, `tools/list`, `tools/call` and the two error homes over stdio.
2. [The Official MCP SDK](./02-official-mcp-sdk/docs/en.md) — what the decorator does, and a notes server that persists to disk.
3. [Skills and Deferred Loading](./03-skills-and-deferred-loading/docs/en.md) — a cheap index in context and bodies or schemas loaded on demand.
4. [The Repo Map](./04-repo-map/docs/en.md) — symbols with line numbers, and chunks cut on structure.
5. [A search_code Tool](./05-search-code-tool/docs/en.md) — ranked `path:line` hits behind one tool.

## Where the depth lives

| If you want | Read |
| --- | --- |
| MCP and standard connectors in product terms | [MCP and standard connectors](../../../api-integrations/mcp-and-standard-connectors.md) |
| Protocols between agents and tools | [Multi-agent and protocols](../../../agentic-ai/multi-agent-and-protocols.md) |
| Tool contracts and reliability | [Tool contracts and reliability](../../../tool-calling/tool-contracts-and-reliability.md) |
| Chunking and ingestion for retrieval | [Chunking and ingestion](../../../rag-vector-databases/chunking-and-ingestion.md) |
| Embeddings and semantic search | [Embeddings and semantic search](../../../rag-vector-databases/embeddings-and-semantic-search.md) |
| What goes into a context pipeline | [The anatomy of a context pipeline](../../../context-engineering/the-anatomy-of-a-context-pipeline.md) |

## Test yourself

1. **A client sends `tools/list` before `notifications/initialized`. What should a careful server do?**
   <details><summary>Answer</summary>It may refuse, because the handshake is not finished. The spec tells clients not to send requests other than pings before `initialize` is answered. It does not say how a server must react. The lesson's server returns a JSON-RPC error. The client must send `initialize`, read the reply, then send the `initialized` notification. (<a href="./01-mcp-protocol-server-client/docs/en.md">Lesson 1</a>)</details>
2. **A tool divides by zero. Is that a JSON-RPC error or a tool result? Why does it matter?**
   <details><summary>Answer</summary>It is a normal result with `isError: true`. The model reads results and can recover. A JSON-RPC error is for protocol faults such as an unknown tool, and many clients do not show it to the model. (<a href="./01-mcp-protocol-server-client/docs/en.md">Lesson 1</a>)</details>
3. **Why does a stray `print` break a stdio MCP server?**
   <details><summary>Answer</summary>The client parses every stdout line as a protocol message. The server must write only valid messages to stdout and send logs to stderr. (<a href="./01-mcp-protocol-server-client/docs/en.md">Lesson 1</a>)</details>
4. **What does an SDK tool decorator derive from your function, and what must you still write well?**
   <details><summary>Answer</summary>It derives the `inputSchema` from type hints and the description from the docstring. You still write the name, hints and docstring, because the model reads them to pick and call the tool. (<a href="./02-official-mcp-sdk/docs/en.md">Lesson 2</a>)</details>
5. **When does a memory MCP server keep notes across restarts?**
   <details><summary>Answer</summary>Only when it writes them somewhere durable, such as a file. A Python list lives and dies with the process. (<a href="./02-official-mcp-sdk/docs/en.md">Lesson 2</a>)</details>
6. **What is always in context for a skill, and what loads later? Why does the description matter so much?**
   <details><summary>Answer</summary>The name and description are always in context. The body loads when the skill is used. The description is all the model sees when it decides, so it must name concrete cases. (<a href="./03-skills-and-deferred-loading/docs/en.md">Lesson 3</a>)</details>
7. **Why must a chunker handle decorators and nested definitions?**
   <details><summary>Answer</summary>A chunk that drops its decorators is not the real definition, and a flat walk loses the parent of a method. Qualified names such as `Session.open` keep the parent. (<a href="./04-repo-map/docs/en.md">Lesson 4</a>)</details>
8. **Why should `search_code` return `path:line` hits and not file contents, and what should it do when nothing matches?**
   <details><summary>Answer</summary>Hits keep the answer small, and the agent reads the lines it needs. With no match the tool must return an empty result, so the agent does not follow a weak "closest" hit. (<a href="./05-search-code-tool/docs/en.md">Lesson 5</a>)</details>
