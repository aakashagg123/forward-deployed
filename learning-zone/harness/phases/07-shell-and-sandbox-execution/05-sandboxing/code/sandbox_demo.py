"""Minimal sandbox layer: resource limits + stripped env + restricted cwd.

The deeper layers (namespaces, seccomp, containers) are OS-level; this is the
cheapest containment you can apply from Python. Linux/macOS only (uses `resource`).

Run:  python3 sandbox_demo.py
"""
import os
import resource
import subprocess


def run_limited(command, workdir, cpu_seconds=5, max_mem_mb=256):
    def set_limits():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        soft = max_mem_mb * 1024 * 1024
        try:
            resource.setrlimit(resource.RLIMIT_AS, (soft, soft))
        except (ValueError, OSError):
            pass                                              # not enforceable everywhere
    env = {"PATH": "/usr/bin:/bin", "HOME": workdir}         # minimal env, no secrets
    p = subprocess.run(command, shell=True, cwd=workdir, env=env,
                       preexec_fn=set_limits, capture_output=True, text=True)
    return {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


if __name__ == "__main__":
    import tempfile
    print(run_limited("echo sandboxed && pwd", tempfile.mkdtemp())["stdout"])
