# A bash tool: capture stdout, stderr, exit code

> **Motto** — Running a command means capturing all three of its outputs: stdout, stderr, and exit code.

*Part of Phase 07 — Shell & Sandbox Execution.*

## The Problem

The Bash tool is the agent's most powerful and most dangerous capability. It can run tests,
build, install, and also `rm -rf`. The first requirement is to run a command and capture its
*full* result: stdout, stderr (errors often go there), and the exit code (the only reliable
success signal). An agent that only sees stdout will think a failing build succeeded.

## The Concept

<style>
.dgm-bt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-bt-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-bt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-bt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-bt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-bt-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-bt-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-bt-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-bt-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-bt-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-bt-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-bt-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-bt{padding:20px 16px 18px}.dgm-bt-row{flex-direction:column}}
.dgm-bt-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dgm-bt-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-bt-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-bt-col.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-bt-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-bt-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-bt-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-bt-col.neutral h6{color:#59636e}
.dgm-bt-col.accent h6{color:#0d5c0d}
.dgm-bt-col.blue h6{color:#0550ae}
.dgm-bt-col.green h6{color:#1a614f}
.dgm-bt-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-bt-item:last-child{margin-bottom:0}
.dgm-bt-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-bt{padding:20px 16px 18px}.dgm-bt-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-bt">
  <span class="dgm-bt-chip">Three streams, one structured result</span>
  <h4>stdout, stderr, and exit code all combine before the model sees any of it</h4>
  <p class="dgm-bt-sub">The model reasons about one result object, not three separate streams.</p>
  <div class="dgm-bt-row">
    <div class="dgm-bt-n neutral">Command</div>
    <span class="dgm-bt-arr">→</span>
    <div class="dgm-bt-n accent">Run in a shell</div>
  </div>
  <div class="dgm-bt-cols">
    <div class="dgm-bt-col blue">
      <h6>stdout</h6>
    </div>
    <div class="dgm-bt-col accent">
      <h6>stderr</h6>
    </div>
    <div class="dgm-bt-col green">
      <h6>Exit code</h6>
    </div>
  </div>
  <div class="dgm-bt-link">↓ one structured result → model</div>
</div>


Exit code 0 means success, and any nonzero code means failure. The model needs all three
signals to reason about what happened.

## Build It

`code/bash_tool.py` — capture everything with `subprocess`:

```python
import subprocess

def run(command, cwd=None):
    proc = subprocess.run(command, shell=True, cwd=cwd,
                          capture_output=True, text=True)
    return {"stdout": proc.stdout, "stderr": proc.stderr, "exit_code": proc.returncode}

def format_result(r, max_chars=4000):
    out = r["stdout"] + (("\n[stderr]\n" + r["stderr"]) if r["stderr"] else "")
    if len(out) > max_chars:
        out = out[:max_chars] + f"\n…[truncated]"
    return f"exit={r['exit_code']}\n{out}"
```

```python
print(format_result(run("echo hello && echo oops 1>&2")))
print(format_result(run("exit 3")))     # exit=3
```

The result is one structured block the model reads. Exit code comes first, so failure is
obvious. Output is truncated (Phase 3 L3), so a noisy command can't blow the budget.

## Use It

This is the **Bash** tool in Claude Code / Codex. It runs your command and returns combined
output with the exit status. Because the exit code is captured, the agent can tell a passing
test run from a failing one. Phrase tasks so the agent *checks* exit codes ("run the tests
and fix failures") rather than eyeballing stdout.

## Ship It

[`code/bash_tool.py`](../../01-bash-tool/code/bash_tool.py) — a command runner capturing
stdout/stderr/exit code with truncation.

## Check Yourself

**Q1.** Why capture the exit code, not just stdout?

- A) style
- B) the exit code is the reliable success/failure signal; stdout alone can mislead
- C) speed
- D) no reason

<details><summary>Answer</summary>B — nonzero exit = failure, even if stdout looks
fine.</details>

**Q2.** Why capture stderr separately?

- A) it's optional
- B) errors and warnings often go to stderr, not stdout
- C) to sort output
- D) no reason

<details><summary>Answer</summary>B — stderr carries the error detail.</details>

**Challenge.** Add a `combined` mode that interleaves stdout and stderr in real time
order (hint: redirect `2>&1`), and note when that's better vs. keeping them separate.

## Related

- Builds on: Phase 3 — [Results & errors](../../../03-tool-engineering/03-results-and-errors/docs/en.md)
- Next: [Timeouts & killing runaway processes](../../02-timeouts/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
