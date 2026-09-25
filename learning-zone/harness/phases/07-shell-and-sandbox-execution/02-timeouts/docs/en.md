# Timeouts & killing runaway processes

> **Motto** — Every command gets a deadline; a hung process must die, not block the agent forever.

*Part of Phase 07 — Shell & Sandbox Execution.*

## The Problem

A command can hang: a test waiting on input, a server that never exits, an infinite loop.
Without a timeout, the agent blocks indefinitely and the whole session stalls. The bash tool
must impose a **deadline**. On expiry, it must **kill** the process and its children
cleanly, and return a timeout result the model can react to.

## The Concept

<style>
.dgm-to{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-to-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-to h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-to-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-to-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-to-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-to-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-to-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-to-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-to-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-to-b.accent h6{color:#0d5c0d}
.dgm-to-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-to-b.blue h6{color:#0550ae}
.dgm-to-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-to-b.green h6{color:#1a614f}
.dgm-to-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-to-b.red h6{color:#82061e}
.dgm-to-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-to-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-to{padding:20px 16px 18px}.dgm-to-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-to">
  <span class="dgm-to-chip">A deadline the process can't ignore</span>
  <h4>Finish in time and you get the result; miss it and the whole group gets killed</h4>
  <p class="dgm-to-sub">Killing the process group, not just the process, is what stops orphaned children.</p>
  <div class="dgm-to-q">Run with timeout T — finished &lt; T?</div>
  <div class="dgm-to-branches">
    <div class="dgm-to-b green">
      <h6>Yes</h6>
      <p>Return result</p>
    </div>
    <div class="dgm-to-b red">
      <h6>No</h6>
      <p>Kill process group → return timeout</p>
    </div>
  </div>
</div>


Killing the process *group* matters. A shell command may spawn children that outlive the
parent if you kill only the parent.

## Build It

`code/timeout_run.py` — run with a deadline, kill the group on expiry:

```python
import subprocess, os, signal

def run(command, timeout=10):
    proc = subprocess.Popen(command, shell=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True)               # own process group
    try:
        out, err = proc.communicate(timeout=timeout)
        return {"exit_code": proc.returncode, "stdout": out, "stderr": err}
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)           # kill the whole group
        proc.communicate()
        return {"exit_code": -1, "stdout": "", "stderr": f"timeout after {timeout}s"}
```

```python
print(run("echo quick", timeout=5))          # normal result
print(run("sleep 30", timeout=1))            # timeout after 1s, process killed
```

`start_new_session=True` puts the command in its own group, so `killpg` reaps children too.
No orphaned `sleep` processes or servers are left running.

## Use It

The **Bash** tool in Claude Code / Codex takes a timeout, with a default and a max, and
kills commands that exceed it. That's why you can set a generous timeout for a slow build,
and the agent still never hangs forever. For genuinely long-running things, like a dev
server, don't raise the timeout — background it instead (next lesson).

## Ship It

[`code/timeout_run.py`](../../02-timeouts/code/timeout_run.py) — a timeout runner that kills
the process group on expiry.

## Check Yourself

**Q1.** Why kill the process *group*, not just the parent?

- A) it's faster
- B) the command may spawn children that survive if only the parent is killed
- C) the OS requires it
- D) no reason

<details><summary>Answer</summary>B — group kill reaps orphaned children.</details>

**Q2.** A command needs to run for an hour (a dev server). You should…

- A) raise the timeout to an hour
- B) run it as a background task (next lesson), not block the loop
- C) skip the timeout
- D) split it

<details><summary>Answer</summary>B — background long-running processes.</details>

**Challenge.** Try `SIGTERM` first, wait briefly for graceful shutdown, then `SIGKILL` —
a kinder kill sequence.

## Related

- Builds on: [Bash tool](../../01-bash-tool/docs/en.md)
- Next: [Background tasks](../../03-background-tasks/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
