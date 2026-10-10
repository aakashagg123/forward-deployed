# Assemble the agent

> **Motto** — Join the parts into one agent, then prove it fixes a real bug, refuses a dangerous command, and stops at its budget.

*Part of Phase 10 — Capstone.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

You built the parts one at a time: a loop, tools, a permission gate, output limits, a todo list, a budget. Parts that pass their own tests can still fail together. A trim can orphan a tool result. A gate can be skipped by one code path. A loop can ignore its budget.

This lesson joins the parts in one file, `code/agent.py`. A test then drives the whole agent against a real temp repo that has a failing test. The test checks the repo, not the agent's words.

## The Concept

<style>
.dgm-ca1{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ca1-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-ca1 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-ca1-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-ca1-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-ca1-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-ca1-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-ca1-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-ca1-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-ca1-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-ca1-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-ca1-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-ca1{padding:20px 16px 18px}.dgm-ca1-row{flex-direction:column}}
.dgm-ca1-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-ca1-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-ca1-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ca1-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ca1-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-ca1-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-ca1-b.accent h6{color:var(--color-text-success)}
.dgm-ca1-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-ca1-b.blue h6{color:var(--color-text-info)}
.dgm-ca1-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-ca1-b.green h6{color:var(--color-text-success)}
.dgm-ca1-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-ca1-b.red h6{color:var(--color-text-danger)}
.dgm-ca1-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-ca1-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-ca1{padding:20px 16px 18px}.dgm-ca1-branches{grid-template-columns:1fr}}
.dgm-ca1-note{margin-top:10px;padding:9px 14px;background:var(--color-background-success-surface);border:1px dashed var(--color-border-success-outline);border-radius:10px;
  font-size:10.5px;color:var(--color-text-success);line-height:1.4}
.dgm-ca1-branches{margin-bottom:10px}
</style>
<div class="dgm-ca1">
  <span class="dgm-ca1-chip">Capstone 1: the smallest agent that can edit code</span>
  <h4>Loop, gated dispatch, clipped output, step budget</h4>
  <p class="dgm-ca1-sub">Every tool call passes the gate. Every result is clipped. Every model call is a step.</p>
  <div class="dgm-ca1-row">
    <div class="dgm-ca1-n neutral">Task</div>
    <span class="dgm-ca1-arr">→</span>
    <div class="dgm-ca1-n accent">Model (scripted or real)</div>
    <span class="dgm-ca1-arr">→</span>
    <div class="dgm-ca1-n blue">Gate: deny, ask, allow</div>
  </div>
  <div class="dgm-ca1-branches" style="margin-top:10px">
    <div class="dgm-ca1-b green">
      <h6>Allow</h6>
      <p>Run tool: read, edit, bash, todo</p>
    </div>
    <div class="dgm-ca1-b red">
      <h6>Deny</h6>
      <p>Denied message (deny rules run first)</p>
    </div>
  </div>
  <div class="dgm-ca1-q">Clip output → append result → trim old pairs (pairs stay whole)</div>
  <div class="dgm-ca1-branches">
    <div class="dgm-ca1-b accent">
      <h6>Steps left</h6>
      <p>Back to the model</p>
    </div>
    <div class="dgm-ca1-b neutral">
      <h6>No steps left</h6>
      <p>Stop: budget</p>
    </div>
  </div>
  <div class="dgm-ca1-note">No tool calls → done.</div>
</div>


The model is a function: history in, content blocks out. A scripted model reads the history and picks the next call, so the test needs no API key. A real model plugs into the same slot.

Every tool call passes through the gate. Every result is clipped. Every call to the model counts as a step.

## Build It

Each part comes from an earlier lesson. Read that lesson for the why.

**The loop** ([lesson 1.3](../../../01-foundations-and-the-loop/03-the-agent-loop/docs/en.md)). The loop trims history, calls the model, runs the tools, and appends results. The step budget ends it ([lesson 1.4](../../../01-foundations-and-the-loop/04-stopping-errors-and-recovery/docs/en.md) and [lesson 9.2](../../../09-reliability-evals-and-ops/02-budgets-idempotency-degraded-mode/docs/en.md)).

```python
    def run(self, task):
        history = [{"role": "user", "content": task}]
        for step in range(1, self.max_steps + 1):
            blocks = self.model(trim_history(history, self.max_chars))
            history.append({"role": "assistant", "content": blocks})
            uses = [b for b in blocks if b["type"] == "tool_use"]
            if not uses:
                text = "".join(b.get("text", "") for b in blocks)
                return {"status": "done", "steps": step, "text": text, "history": history}
```

**Tools** ([lesson 2.1](../../../02-tools/01-schemas-registry-and-descriptions/docs/en.md), [5.2](../../../05-files-and-shell/02-edit-write-and-patch/docs/en.md), [5.4](../../../05-files-and-shell/04-bash-and-timeouts/docs/en.md)). `edit` needs exactly one match. Paths must stay inside the repo. `bash` runs one command with a timeout and no shell.

```python
    def edit(self, path, old, new):
        p = self.path(path)
        text = p.read_text()
        if text.count(old) != 1:
            return f"error: {text.count(old)} matches for old; it must match exactly once"
        p.write_text(text.replace(old, new))
        return "ok: edited"
```

**The gate** ([lesson 6.1](../../../06-permissions-and-security/01-permission-gate/docs/en.md)). Rules run in the order deny, ask, allow. Anything unmatched asks. A command that chains `rm` after an allowed test run still hits the deny rule first.

```python
def decide(name, args):
    text = args.get("cmd") or args.get("path") or ""
    for verdict in ("deny", "ask", "allow"):
        if any(v == verdict and t == name and re.search(p, text) for v, t, p in RULES):
            return verdict
    return "ask"
```

**Output limits** ([lesson 3.3](../../../03-context-and-memory/03-trim-and-compact/docs/en.md)). `clip` cuts one huge result. `trim_history` drops the oldest turns two messages at a time. A tool call and its result always leave together, so the model never sees an orphan.

```python
    head, rest, dropped = history[0], history[1:], 0
    while size([head] + rest) > limit and len(rest) > 2:
        rest, dropped = rest[2:], dropped + 1
```

**The todo list** ([lesson 7.1](../../../07-planning-and-subagents/01-todo-list/docs/en.md)). The `todo` tool replaces the whole list each time, so the plan is always one consistent state.

**The test.** `code/test_agent.py` builds a temp repo with a buggy `add()` and a failing test. It checks these things:

- The edit lands and the repo's own tests pass.
- `rm -rf .` is blocked, and the file beside it survives.
- Deny wins over allow in a chained command.
- An `ask` with no approver is refused.
- A path outside the repo is refused.
- A model that loops forever stops at the step budget, with every call answered.
- Trimming keeps pairs whole at every limit.

The tests were checked by breaking the agent on purpose. With the `rm` deny rule removed, the blocked-command test fails. With pairs split in `trim_history`, the pair test fails.

## Use It

Run `python3 code/test_agent.py` first. Then read `code/agent_sdk.py`. It replaces `scripted_model` with one function that calls the Anthropic Messages API. `agent.py` already keeps history in the tool-use message format, so the history goes straight to `messages=`. `TOOL_SPECS` goes to `tools=`. The model ID comes from `HARNESS_MODEL`. The `ask` verdict becomes a terminal prompt.

Claude Code has the same parts under other names. It evaluates permission rules in the order deny, ask, allow. It tracks tasks with `TaskCreate`, `TaskGet`, `TaskList`, and `TaskUpdate`, which are on by default only for some models. It bounds print-mode runs with `--max-turns`. Your 150 lines show how each part works.

Before you trust the real agent, run the evals ([lesson 9.3](../../../09-reliability-evals-and-ops/03-eval-harness/docs/en.md)) and record traces ([lesson 9.4](../../../09-reliability-evals-and-ops/04-tracing-and-cost/docs/en.md)).

## Challenge

Make the harness check the model's claim. Before `run` returns `done`, run the test command itself. If the tests fail, append the failure to the history and continue the loop. Write a scripted model that says "done" too early, and assert that the harness does not accept it.

## Sources

[Anthropic Python SDK](https://platform.claude.com/docs/en/api/sdks/python) · [Claude Code tools reference](https://code.claude.com/docs/en/tools-reference) · [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
