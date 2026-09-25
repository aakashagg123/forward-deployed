# Background tasks & long-running commands

> **Motto** — A dev server doesn't block the agent — start it, get a handle, keep working.

*Part of Phase 07 — Shell & Sandbox Execution.*

## The Problem

Some commands are *supposed* to run indefinitely: a dev server, a file watcher, a tail. You
can't run these in the foreground, because they'd block the loop. You also can't
timeout-kill them, because you want them to stay alive. The bash tool needs a
**background** mode: launch the process, return a handle immediately, stream its output to
a log the agent can poll, and let the agent stop it later.

## The Concept

<style>
.dgm-bgt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-bgt-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-bgt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-bgt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-bgt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-bgt-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-bgt-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-bgt-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-bgt-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-bgt-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-bgt-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-bgt-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-bgt{padding:20px 16px 18px}.dgm-bgt-row{flex-direction:column}}
</style>
<div class="dgm-bgt">
  <span class="dgm-bgt-chip">A handle, not a blocking wait</span>
  <h4>Launch, get a handle back immediately, then poll or stop on your own schedule</h4>
  <p class="dgm-bgt-sub">Output goes to a logfile so nothing is lost while the agent does other work.</p>
  <div class="dgm-bgt-row">
    <div class="dgm-bgt-n accent">run(background=True)</div>
    <span class="dgm-bgt-arr">→</span>
    <div class="dgm-bgt-n blue">Launch, redirect output → logfile</div>
    <span class="dgm-bgt-arr">→</span>
    <div class="dgm-bgt-n green">Return handle (pid + log path)</div>
    <span class="dgm-bgt-arr">→</span>
    <div class="dgm-bgt-n ">Agent polls log / checks status</div>
    <span class="dgm-bgt-arr">→</span>
    <div class="dgm-bgt-n red">stop(handle) when done</div>
  </div>
</div>


## Build It

`code/background.py` — a tiny background-job manager:

```python
import subprocess, tempfile, os, signal

class BackgroundJobs:
    def __init__(self):
        self.jobs = {}                         # id -> (proc, logpath)

    def start(self, command):
        log = tempfile.mktemp(suffix=".log")
        f = open(log, "w")
        proc = subprocess.Popen(command, shell=True, stdout=f, stderr=subprocess.STDOUT,
                                start_new_session=True)
        self.jobs[proc.pid] = (proc, log)
        return {"id": proc.pid, "log": log}

    def output(self, job_id):
        _, log = self.jobs[job_id]
        with open(log) as f:
            return f.read()

    def status(self, job_id):
        proc, _ = self.jobs[job_id]
        return "running" if proc.poll() is None else f"exited({proc.returncode})"

    def stop(self, job_id):
        proc, _ = self.jobs[job_id]
        if proc.poll() is None:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        return "stopped"
```

```python
import time
jobs = BackgroundJobs()
h = jobs.start("for i in 1 2 3; do echo line $i; sleep 0.1; done")
time.sleep(0.5)
print(jobs.status(h["id"]), "|", jobs.output(h["id"]).split())
jobs.stop(h["id"])
```

The agent gets a handle instantly. It polls the log to see progress, and stops the job when
the task is done, without ever blocking the loop.

## Use It

This is the **Bash** tool's background mode in Claude Code / Codex (`run_in_background`).
Start a dev server, then keep editing while it runs, read its log to check for errors, and
kill it at the end. Pair it with the timeout runner (lesson 02): use a deadline for short
commands and background mode for long ones.

## Ship It

[`code/background.py`](../../03-background-tasks/code/background.py) — a background-job manager
(start / output / status / stop).

## Check Yourself

**Q1.** Why background a dev server instead of raising the timeout?

- A) it's faster
- B) it should stay alive; backgrounding returns a handle without blocking the loop
- C) timeouts are banned
- D) no reason

<details><summary>Answer</summary>B — long-lived processes belong in the
background.</details>

**Q2.** How does the agent see a background job's progress?

- A) it can't
- B) by polling the job's log file (and checking status)
- C) via stdout only
- D) it waits for exit

<details><summary>Answer</summary>B — output streams to a log it polls.</details>

**Challenge.** Add `wait_for(job_id, pattern, timeout)` that blocks until a line matching
`pattern` appears in the log (e.g. "Listening on") or times out.

## Related

- Builds on: [Timeouts](../../02-timeouts/docs/en.md)
- Next: [Working-directory & shell-state pitfalls](../../04-cwd-and-state/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
