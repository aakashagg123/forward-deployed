# Working-directory & shell-state pitfalls

> **Motto** — Each command runs in a fresh shell — `cd` doesn't persist unless the harness makes it.

*Part of Phase 07 — Shell & Sandbox Execution.*

## The Problem

Here is a subtle, common bug: the agent runs `cd backend`, then `npm test`, and the test
runs in the *wrong* directory. Why? Each tool call spawns a new shell, so environment
changes — `cd`, `export`, activated venvs — **don't persist** between calls. If the harness
doesn't track working directory and env itself, multi-step shell workflows silently break.

## The Concept

<style>
.dgm-cws{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-cws-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-cws h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-cws-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-cws-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-cws-branches{display:grid;grid-template-columns:repeat(1,1fr);gap:10px}
.dgm-cws-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-cws-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-cws-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-cws-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-cws-b.accent h6{color:#0d5c0d}
.dgm-cws-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-cws-b.blue h6{color:#0550ae}
.dgm-cws-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-cws-b.green h6{color:#1a614f}
.dgm-cws-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-cws-b.red h6{color:#82061e}
.dgm-cws-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-cws-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-cws{padding:20px 16px 18px}.dgm-cws-branches{grid-template-columns:1fr}}
.dgm-cws-chain{display:flex;flex-direction:column;gap:2px}
.dgm-cws-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-cws-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-cws-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-cws{padding:20px 16px 18px}}
</style>
<div class="dgm-cws">
  <span class="dgm-cws-chip">Every call is a fresh shell unless the harness intervenes</span>
  <h4>cd in call 1 doesn't survive to call 2 — not without tracked state</h4>
  <p class="dgm-cws-sub">The harness has to inject cwd and env into every run to fake persistence.</p>
  <div class="dgm-cws-branches">
    <div class="dgm-cws-b red">
      <h6>Without tracking</h6>
      <p>Call 1: cd backend — new shell, state lost → Call 2: npm test runs in repo root!</p>
    </div>
  </div>
  <div class="dgm-cws-chain">
    <div class="dgm-cws-node accent">Harness tracks cwd + env</div>
    <div class="dgm-cws-arr">↓</div>
    <div class="dgm-cws-node alt">Inject into every run</div>
    <div class="dgm-cws-arr">↓</div>
    <div class="dgm-cws-node accent">State persists</div>
  </div>
</div>


The fix: the harness keeps a session `cwd` and env, and applies them to each command. Or you
write compound commands (`cd backend && npm test`), so state lives within one call.

## Build It

`code/shell_session.py` — a session that persists cwd across calls:

```python
import subprocess, os

class ShellSession:
    def __init__(self, cwd=None, env=None):
        self.cwd = cwd or os.getcwd()
        self.env = dict(os.environ, **(env or {}))

    def run(self, command):
        # Detect a leading `cd X` and update session cwd (simplified).
        if command.strip().startswith("cd "):
            target = command.strip()[3:].strip()
            new = os.path.normpath(os.path.join(self.cwd, target))
            if os.path.isdir(new):
                self.cwd = new
                return {"exit_code": 0, "stdout": f"cwd={self.cwd}", "stderr": ""}
            return {"exit_code": 1, "stdout": "", "stderr": f"no such dir: {target}"}
        p = subprocess.run(command, shell=True, cwd=self.cwd, env=self.env,
                           capture_output=True, text=True)
        return {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
```

```python
import tempfile, os
d = tempfile.mkdtemp(); os.mkdir(os.path.join(d, "sub"))
s = ShellSession(cwd=d)
s.run("cd sub")
print(s.run("pwd")["stdout"].strip().endswith("/sub"))   # True — cwd persisted
```

Now `cd` "sticks" across calls because the session owns the working directory, not the
ephemeral shell.

## Use It

In Claude Code / Codex, the shell environment **doesn't** persist between Bash calls. This
is documented behavior. The practical rule: use absolute paths, or chain commands with `&&`
in one call, rather than relying on a prior `cd`. The session pattern here is what a custom
harness builds to make state persist deliberately.

## Ship It

[`code/shell_session.py`](../../04-cwd-and-state/code/shell_session.py) — a shell session that
persists working directory across calls.

## Check Yourself

**Q1.** After `cd backend` in one Bash call, the next call runs in…

- A) backend
- B) the original directory — shell state doesn't persist between calls
- C) the home directory
- D) a random directory

<details><summary>Answer</summary>B — each call is a fresh shell.</details>

**Q2.** A reliable way to run a command in a subdir in one call is…

- A) `cd subdir` then a separate call
- B) `cd subdir && command` (compound) or an absolute path
- C) hope
- D) export a variable

<details><summary>Answer</summary>B — keep state within one call.</details>

**Challenge.** Extend the session to also persist `export VAR=value` across calls (track env
the way it tracks cwd).

## Related

- Builds on: [Bash tool](../../01-bash-tool/docs/en.md)
- Next: [Sandboxing](../../05-sandboxing/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
