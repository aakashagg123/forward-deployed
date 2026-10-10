# Parallel Tool Use

> **Motto** — One model turn can ask for several tools at once, so run them together when it is safe and answer them all in one message.

*Part of Phase 02 — Tools.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

The loop so far ran one tool per turn. A real model often asks for several in one message: read three files, or check two services. The API expects a result for every `tool_use` block. If you answer only the first, the request fails.

Running them one after another is also slow. Three reads that could overlap take three times as long. But running everything at once is unsafe for tools that write.

## The Concept

The API does not prescribe an order. You choose. Independent, read-only calls are usually safe to run in parallel. Calls with side effects, shared state, or an ordering need run one at a time.

Whatever you choose, return one `tool_result` per `tool_use`. Put them all in the next user message. Put every `tool_result` before any text. If you skip a call, still answer it with an `is_error` result that says why.

Do not send each result in its own user message. That pattern teaches the model to stop making parallel calls.

<style>
.dgm-spt{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-spt-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-spt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-spt-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-spt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-spt-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-spt-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-spt-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-spt-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-spt-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-spt-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-spt-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-spt{padding:20px 16px 18px}.dgm-spt-row{flex-direction:column}}
</style>
<div class="dgm-spt">
  <span class="dgm-spt-chip">Parallel tool calls resolve as one user turn</span>
  <h4>Several tool_use blocks in, one tool_result batch out</h4>
  <p class="dgm-spt-sub">Each call is validated, run and wrapped independently, but they return together.</p>
  <div class="dgm-spt-row">
    <div class="dgm-spt-n neutral">Assistant turn</div>
    <span class="dgm-spt-arr">→</span>
    <div class="dgm-spt-n accent">[tool_use, tool_use, …]</div>
    <span class="dgm-spt-arr">→</span>
    <div class="dgm-spt-n blue">Run each (validate, run, wrap)</div>
    <span class="dgm-spt-arr">→</span>
    <div class="dgm-spt-n green">One user turn: [tool_result, tool_result, …]</div>
  </div>
</div>


## Build It

`code/parallel_tools.py` has three small functions. `outcome` runs one call and turns a crash into an error result. In a full harness it would call `run_tool` from [Validation, Results and Errors](../../02-validation-results-and-errors/docs/en.md).

```python
def outcome(call, impls):
    """Run one call. A crash becomes an error result, never an exception."""
    try:
        text, is_error = str(impls[call["name"]](**call["input"])), False
    except Exception as exc:
        text, is_error = f"{type(exc).__name__}: {exc}", True
    return {"type": "tool_result", "tool_use_id": call["id"], "content": text, "is_error": is_error}
```

`run_batch` picks the mode. All-read-only batches go to a thread pool, and `pool.map` keeps the call order. Any other batch runs in order, and a failure skips the rest with an explanation.

```python
def run_batch(calls, impls, read_only):
    """Return one tool_result per call, in call order."""
    if all(c["name"] in read_only for c in calls):
        with ThreadPoolExecutor(max_workers=len(calls)) as pool:   # independent reads
            return list(pool.map(lambda c: outcome(c, impls), calls))
    results = []
    for n, call in enumerate(calls):                               # side effects: in order
        res = outcome(call, impls)
        results.append(res)
        if res["is_error"]:                                        # skip the rest, but still answer
            for rest in calls[n + 1:]:
                results.append({"type": "tool_result", "tool_use_id": rest["id"], "is_error": True,
                                "content": f"Not executed: the earlier {call['name']} call failed."})
            break
    return results
```

`user_turn` builds the single user message with results first and text last.

```python
def user_turn(results, note=None):
    """All results go in ONE user message. tool_result blocks come first, any text after."""
    content = list(results) + ([{"type": "text", "text": note}] if note else [])
    return {"role": "user", "content": content}
```

The proof of parallelism is a barrier. Three reads each wait for the other two. Run one after another, they would time out. They pass only because all three run at once. The other asserts check that result order is kept, that text follows the results, and that a failed write skips the next one.

## Use It

`code/parallel_tools_sdk.py` wires `run_batch` into the SDK loop. It needs `pip install anthropic` and `ANTHROPIC_API_KEY`.

Current models call tools in parallel by default when it helps. To push them further, add a line to the system prompt. This line comes from Anthropic's guidance:

```python
SYSTEM = ("For maximum efficiency, whenever you need to perform multiple independent "
          "operations, invoke all relevant tools simultaneously rather than sequentially.")
```

To turn parallel calls off, set `disable_parallel_tool_use: true` inside `tool_choice`. It is not a top-level parameter. With `auto`, the model then makes at most one tool call per response.

## Challenge

Give each read a 5-second limit. If one read is too slow, return an `is_error` result for that call only. The other results must still return in the same user message.

## Sources

[Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use)

Next: [Context Budget](../../../03-context-and-memory/01-context-budget/docs/en.md)
