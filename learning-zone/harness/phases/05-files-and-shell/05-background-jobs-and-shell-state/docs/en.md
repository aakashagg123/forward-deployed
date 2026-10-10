# Background Jobs and Shell State

> **Motto** — A dev server must not block the agent, and a `cd` must not vanish between calls.

*Part of Phase 05 — Files and Shell.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

Two bugs hit every shell tool.

First, some commands should run for a long time. A dev server, a file watcher and a `tail` never exit on their own. A foreground call would block the loop. A timeout would kill them, and you want them alive.

Second, the agent runs `cd backend` and then `npm test`. The test runs in the wrong folder. A harness that uses one `subprocess.run` per call starts a new shell each time. It loses the working directory (cwd) and every `export`.

## The Concept

<style>
.dgm-bgt{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-bgt-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-bgt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-bgt-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-bgt-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-bgt-lane{font-size:9.5px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary);text-align:center;margin:0 0 6px}
.dgm-bgt-lane.gap{margin-top:16px}
.dgm-bgt-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-bgt-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-bgt-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-bgt-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-bgt-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-bgt-b.accent h6{color:var(--color-text-success)}
.dgm-bgt-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-bgt-b.blue h6{color:var(--color-text-info)}
.dgm-bgt-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-bgt-b.green h6{color:var(--color-text-success)}
.dgm-bgt-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-bgt-b.red h6{color:var(--color-text-danger)}
.dgm-bgt-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-bgt-b.neutral h6{color:var(--color-text)}
.dgm-bgt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-bgt-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-bgt-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-bgt-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-bgt-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-bgt-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-bgt-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-bgt-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
.dgm-bgt-split{display:flex;flex-direction:column;gap:6px}
.dgm-bgt-note{font-size:10px;color:var(--color-text-secondary);text-align:center;margin:8px 0 0}
@media (max-width:640px){.dgm-bgt{padding:20px 16px 18px}.dgm-bgt-branches{grid-template-columns:1fr}.dgm-bgt-row{flex-direction:column}}
</style>
<div class="dgm-bgt">
  <span class="dgm-bgt-chip">A handle, and a shell that remembers</span>
  <h4>Jobs return a handle; the shell keeps cwd but not env</h4>
  <p class="dgm-bgt-sub">Output goes to a log file, so nothing is lost while the agent does other work.</p>
  <p class="dgm-bgt-lane">Background job</p>
  <div class="dgm-bgt-row">
    <div class="dgm-bgt-n accent">run(background=True)</div>
    <span class="dgm-bgt-arr">→</span>
    <div class="dgm-bgt-n blue">Launch, output to log file</div>
    <span class="dgm-bgt-arr">→</span>
    <div class="dgm-bgt-n green">Return handle (id + log path)</div>
    <span class="dgm-bgt-arr">→</span>
    <div class="dgm-bgt-n ">Agent polls log, checks status</div>
    <span class="dgm-bgt-arr">→</span>
    <div class="dgm-bgt-n red">stop(handle) when done</div>
  </div>
  <p class="dgm-bgt-lane gap">Shell state: next Bash call</p>
  <div class="dgm-bgt-branches">
    <div class="dgm-bgt-b green">
      <h6>cd inside project</h6>
      <p>cwd carries over</p>
    </div>
    <div class="dgm-bgt-b red">
      <h6>cd outside project</h6>
      <p>Reset to project dir, with a note</p>
    </div>
    <div class="dgm-bgt-b red">
      <h6>export VAR</h6>
      <p>Env var dropped. Use an env file.</p>
    </div>
  </div>
</div>


A background job returns a handle at once. Output goes to a log file. The agent polls the log, waits for a ready line such as `Listening on`, and stops the job at the end.

Shell state has two parts, and they behave differently in Claude Code. The cwd carries over between calls, if it stays inside the project. Environment variables do not carry over. A harness must decide each part on purpose.

## Build It

`code/background.py` is a small job manager. `stop` signals the whole process group, because a shell may hold children.

```python
class BackgroundJobs:
    def __init__(self):
        self.jobs = {}                                    # id -> (proc, logpath)
        self._next = 1

    def start(self, command):
        fd, log = tempfile.mkstemp(suffix=".log")
        with os.fdopen(fd, "w") as f:                     # the child keeps its own copy of the fd
            proc = subprocess.Popen(command, shell=True, stdin=subprocess.DEVNULL,
                                    stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
        job_id = f"job{self._next}"
        self._next += 1
        self.jobs[job_id] = (proc, log)
        return {"id": job_id, "pid": proc.pid, "log": log}

    def output(self, job_id):
        with open(self.jobs[job_id][1]) as f:
            return f.read()

    def status(self, job_id):
        proc = self.jobs[job_id][0]
        return "running" if proc.poll() is None else f"exited({proc.returncode})"

    def wait_for(self, job_id, pattern, timeout=5):
        """Block until a log line matches pattern (for example 'Listening on')."""
        end = time.time() + timeout
        while time.time() < end:
            if re.search(pattern, self.output(job_id)):
                return True
            if self.status(job_id) != "running":
                return bool(re.search(pattern, self.output(job_id)))
            time.sleep(0.05)
        return False

    def stop(self, job_id):
        proc = self.jobs[job_id][0]
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)           # the whole group, not only the shell
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
        return self.status(job_id)
```

`code/shell_session.py` keeps the cwd and drops the env. It sets a shell `EXIT` trap that writes the final directory to a file. This works for `cd src && make`, which a "does the command start with `cd`" check would miss. A `cd` outside the project is undone with a note. An optional `env_file` is sourced before every call, so chosen variables persist.

```python
class ShellSession:
    def __init__(self, project_dir, env_file=None):
        self.root = os.path.realpath(project_dir)
        self.cwd = self.root
        self.env_file = env_file            # sourced before every command (like CLAUDE_ENV_FILE)

    def run(self, command, timeout=10):
        fd, state = tempfile.mkstemp()
        os.close(fd)
        script = f"trap 'pwd -P > {state}' EXIT\n"        # record where the command ended
        if self.env_file:
            script += f". {self.env_file}\n"
        script += command + "\n"
        p = subprocess.run(["bash", "-c", script], cwd=self.cwd, capture_output=True,
                           text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        with open(state) as f:
            end = f.read().strip()
        os.remove(state)
        note = ""
        if end == self.root or end.startswith(self.root + os.sep):
            self.cwd = end                                # cd inside the project sticks
        else:
            self.cwd = self.root                          # cd outside the project is undone
            note = f"\nShell cwd was reset to {self.root}"
        return {"exit_code": p.returncode, "stdout": p.stdout + note, "stderr": p.stderr}
```

Both files end with asserts. The jobs file checks that `start` does not block, that `wait_for` can fail, that `stop` ends the group, and that a failing job reports its exit code. The session file checks that a plain `subprocess.run` loses the cwd, that `export` is lost, and that the env file survives.

## Use It

Claude Code's **Bash** tool behaves like this session. Verified from the docs:

- A `cd` in the main session carries over to later Bash commands while it stays inside the project or an added directory. Outside, Claude Code resets to the project directory and appends `Shell cwd was reset to <dir>`.
- Subagent sessions never carry over cwd changes.
- `export` does not persist. To keep variables, point `CLAUDE_ENV_FILE` at a shell script, or fill it from a `SessionStart` hook.
- Aliases and functions from your shell startup file are available.

For background work, Claude sets `run_in_background: true`. In unattended runs (`-p`, the Agent SDK, CI, cloud), a background command has a 30-minute limit by default and 2 hours at most. A local interactive session has no such limit (v2.1.288 and later; earlier versions applied it everywhere). List and stop tasks with `/tasks`. A `cd` inside a backgrounded command never applies to later commands.

## Challenge

Add a `restart(job_id)` to `BackgroundJobs` that stops a job and starts the same command again. Assert that the new job has a new id, a new log, and a fresh PID. Then say when a harness should refuse a restart, for example after a crash loop.

## Sources

Claude Code docs, "Tools reference", sections "What persists between commands" and "Background commands" (code.claude.com/docs/en/tools-reference).

Next: [Sandbox and Egress](../../06-sandbox-and-egress/docs/en.md)
