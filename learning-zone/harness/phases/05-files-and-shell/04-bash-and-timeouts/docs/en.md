# Bash: Capture Everything and Set a Deadline

> **Motto** — A command gives three signals (stdout, stderr, exit code) and needs a deadline, or one hung process stalls the agent.

*Part of Phase 05 — Files and Shell.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

The Bash tool is the agent's strongest tool. It runs tests and builds. It can also run `rm -rf`. The safety side comes later. This lesson covers the first two needs.

First, the model must see the full result. stderr often holds the error. The exit code is the only reliable pass or fail signal. An agent that sees only stdout may call a failed build a success.

Second, a command can hang. A test may wait for input. A server may never exit. Without a deadline the whole session stalls.

## The Concept

<style>
.dgm-bt{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-bt-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-bt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-bt-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-bt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-bt-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-bt-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-bt-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-bt-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-bt-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-bt-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-bt-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-bt{padding:20px 16px 18px}.dgm-bt-row{flex-direction:column}}
.dgm-bt-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dgm-bt-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-bt-col.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-bt-col.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-bt-col.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-bt-col.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-bt-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-bt-col.neutral h6{color:var(--color-text-secondary)}
.dgm-bt-col.accent h6{color:var(--color-text-success)}
.dgm-bt-col.blue h6{color:var(--color-text-info)}
.dgm-bt-col.green h6{color:var(--color-text-success)}
.dgm-bt-item{background:var(--color-surface);border:1px solid var(--color-border-info-surface);border-radius:8px;padding:6px 9px;font-size:10px;
  color:var(--color-text);line-height:1.35;margin-bottom:5px}
.dgm-bt-item:last-child{margin-bottom:0}
.dgm-bt-link{display:flex;justify-content:center;color:var(--color-text-tertiary);font-size:9.5px;font-weight:700;
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


Exit code 0 means success. Any other code means failure. The result block puts the status first, so failure is hard to miss.

A deadline needs a real kill. A shell command may start children. If you kill only the shell, the children live on. So the tool starts the command in its own **process group** and kills the whole group on expiry.

Output needs a cap too. Keep the head and the tail of long output. The start shows what ran. The end shows how it failed.

## Build It

`code/bash_tool.py` has `run` and `format_result`:

```python
def run(command, cwd=None, timeout=10):
    proc = subprocess.Popen(
        command, shell=True, cwd=cwd, text=True,
        stdin=subprocess.DEVNULL,                     # a command that waits for input gets EOF
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True)                       # own process group
    try:
        out, err = proc.communicate(timeout=timeout)
        return {"exit_code": proc.returncode, "stdout": out, "stderr": err, "timed_out": False}
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)           # kill the shell AND its children
        out, err = proc.communicate()
        return {"exit_code": -1, "stdout": out or "", "stderr": (err or "") + f"\ntimeout after {timeout}s",
                "timed_out": True}


def format_result(r, max_chars=400):
    """One block for the model. Exit code first. Keep the head and the tail of long output."""
    body = r["stdout"] + (("\n[stderr]\n" + r["stderr"]) if r["stderr"].strip() else "")
    if len(body) > max_chars:
        half = max_chars // 2
        cut = len(body) - max_chars
        body = body[:half] + f"\n...[{cut} chars cut]...\n" + body[-half:]
    status = "TIMEOUT" if r["timed_out"] else f"exit={r['exit_code']}"
    return f"{status}\n{body}".rstrip()
```

`start_new_session=True` gives the command its own group, so `os.killpg` reaches every child. `stdin=DEVNULL` makes a command that waits for input read end-of-file at once, so it cannot hang.

The asserts check each part. They capture all three signals. They start `sleep 30 &`, hit the deadline, and then check that the child process is gone. They also check that long output keeps both ends. Run `python3 code/bash_tool.py`.

## Use It

Claude Code's **Bash** tool has the same three parts, with some differences.

**Timeout.** The default is two minutes and the ceiling is ten minutes. The variables are `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`. Claude passes a `timeout` on a call when it needs more. A foreground command that hits its timeout is not killed. Claude Code moves it to the background, unless the command starts with `sleep`. The [next lesson](../../05-background-jobs-and-shell-state/docs/en.md) covers background jobs.

**Output.** A valid result arrives inline up to about 30,000 characters. Past that, Claude gets a file path and a preview of the first 2,000 characters. A failure result keeps about 10,000 characters as a head and tail excerpt.

**Exit codes.** Exit code 1 counts as success for commands such as `grep`, `rg`, `find`, `diff`, `test` and `git diff`, because it means "no match" or "differs". Any other command that exits 1 counts as a failure. Your harness may need the same table.

## Challenge

Change the kill to a gentler sequence. Send `SIGTERM` to the group, wait one second, then send `SIGKILL`. Write a command that traps `SIGTERM` and cleans up a file. Assert that the file is cleaned up.

## Sources

Claude Code docs, "Tools reference", section "Bash tool behavior" (code.claude.com/docs/en/tools-reference).

Next: [Background Jobs and Shell State](../../05-background-jobs-and-shell-state/docs/en.md)
