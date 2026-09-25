# Sandboxing: containers, namespaces, seccomp

> **Motto** — Give the agent a room it can't escape, not the keys to the whole house.

*Part of Phase 07 — Shell & Sandbox Execution.*

## The Problem

The bash tool runs arbitrary commands the model chose, and untrusted content may have
influenced that choice (Phase 17). Even with permission gating, you want a *containment*
layer, so a bad command can't read your SSH keys, wipe your home directory, or call out to
the internet. That layer is the sandbox: filesystem, process, and network isolation around
execution.

## The Concept

<style>
.dgm-sbx{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-sbx-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-sbx h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-sbx-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-sbx-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-sbx-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-sbx-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-sbx-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-sbx-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-sbx-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-sbx-b.accent h6{color:#0d5c0d}
.dgm-sbx-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-sbx-b.blue h6{color:#0550ae}
.dgm-sbx-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-sbx-b.green h6{color:#1a614f}
.dgm-sbx-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-sbx-b.red h6{color:#82061e}
.dgm-sbx-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-sbx-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-sbx{padding:20px 16px 18px}.dgm-sbx-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-sbx">
  <span class="dgm-sbx-chip">Three boundaries around every agent command</span>
  <h4>Filesystem, process, and network are each constrained independently</h4>
  <p class="dgm-sbx-sub">Egress policy gets its own lesson next — it's the boundary that changes most per deployment.</p>
  <div class="dgm-sbx-q">Sandbox</div>
  <div class="dgm-sbx-branches">
    <div class="dgm-sbx-b accent">
      <h6>Filesystem</h6>
      <p>Only the workspace is writable</p>
    </div>
    <div class="dgm-sbx-b blue">
      <h6>Process</h6>
      <p>Resource limits, no escalation (seccomp)</p>
    </div>
    <div class="dgm-sbx-b green">
      <h6>Network</h6>
      <p>Egress policy (next lesson)</p>
    </div>
  </div>
</div>


The layers run from weakest to strongest: a separate working directory, OS resource limits,
Linux namespaces or seccomp, and full containers or VMs. More isolation means more safety,
and also more setup.

## Build It / Use It

Real sandboxing is OS-level, so this is **Use It**. `code/sandbox_demo.py` shows the
cheapest useful layer you can apply from Python: run a command with reduced privileges and
resource limits, using `resource` plus a restricted cwd and env. The deeper layers are
containers and namespaces:

```python
import subprocess, resource, os

def run_limited(command, workdir, cpu_seconds=5, max_mem_mb=256):
    def set_limits():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        soft = max_mem_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (soft, soft))
    env = {"PATH": "/usr/bin:/bin", "HOME": workdir}        # minimal env, no secrets
    p = subprocess.run(command, shell=True, cwd=workdir, env=env,
                       preexec_fn=set_limits, capture_output=True, text=True)
    return {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
```

```python
import tempfile
print(run_limited("echo sandboxed && pwd", tempfile.mkdtemp())["stdout"])
```

This caps CPU and memory, and strips the environment down to the workspace. It's a real, if
minimal, containment step. Production harnesses go further, with a container or microVM per
session.

## Use It

This is exactly why **Claude Code on the web / Codex cloud** run in **isolated, ephemeral
containers**. The repo is cloned fresh, execution stays contained, and the box is reclaimed
afterward. Locally, Claude Code uses permission gating (Phase 8) plus OS sandboxing where
available. The takeaway: never run an agent's shell with your full user privileges if you
can contain it instead.

## Ship It

[`code/sandbox_demo.py`](../../05-sandboxing/code/sandbox_demo.py) — a resource-limited,
minimal-env command runner (the first sandbox layer).

## Check Yourself

**Q1.** Why sandbox shell execution even with permission gating?

- A) redundancy is bad
- B) defense in depth — containment limits damage if a bad command slips through
- C) speed
- D) no reason

<details><summary>Answer</summary>B — gating decides *whether*; the sandbox limits *blast
radius*.</details>

**Q2.** The strongest common isolation for an agent session is…

- A) a separate folder
- B) a container or microVM per session
- C) a long prompt
- D) a timeout

<details><summary>Answer</summary>B — containers/VMs give full isolation.</details>

**Challenge.** Add a read-only bind of the repo plus a writable `/tmp` (conceptually), and
list which of your secrets would still be reachable from inside the minimal env.

## Related

- Builds on: [Bash tool](../../01-bash-tool/docs/en.md)
- Next: [Network policies & egress control](../../06-egress-control/docs/en.md)
- Deepens in: Phase 8 — Permissions, Phase 17 — Security
- [Roadmap](../../../../ROADMAP.md)
