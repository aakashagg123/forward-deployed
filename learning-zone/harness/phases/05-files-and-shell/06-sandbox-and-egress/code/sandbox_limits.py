"""The cheapest containment: resource limits, a minimal env, a fixed cwd, a deadline.

This is NOT a sandbox. It does not stop file reads or network use.
Linux and macOS only. Run:  python3 code/sandbox_limits.py
"""
import os
import resource
import signal
import subprocess
import sys
import tempfile


def run_limited(command, workdir, cpu_seconds=2, max_mem_mb=256, max_file_mb=1, timeout=10):
    def set_limits():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        mem = max_mem_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        size = max_file_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (size, size))

    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "HOME": workdir}
    proc = subprocess.Popen(command, shell=True, cwd=workdir, env=env, text=True,
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, preexec_fn=set_limits,
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        return {"exit_code": -1, "stdout": out, "stderr": err + "timeout"}
    return {"exit_code": proc.returncode, "stdout": out, "stderr": err}


if __name__ == "__main__":
    work = tempfile.mkdtemp()
    py = "python3"

    # Minimal env: a secret in the parent process does not reach the child.
    os.environ["SECRET_TOKEN"] = "s3cret"
    out = run_limited("env", work)["stdout"]
    assert "SECRET_TOKEN" not in out and f"HOME={work}" in out

    # CPU limit: a busy loop is killed by SIGXCPU (exit code -24 on Linux) after about 1 second.
    r = run_limited(f'{py} -c "while True: pass"', work, cpu_seconds=1)
    assert r["exit_code"] != 0, r

    # Memory limit: a big allocation fails instead of eating the machine.
    r = run_limited(f'{py} -c "x = bytearray(900*1024*1024)"', work, max_mem_mb=128)
    assert r["exit_code"] != 0 and "MemoryError" in r["stderr"]

    # File-size limit: a 5 MB write is stopped at 1 MB.
    r = run_limited(f'{py} -c "open(\'big\',\'wb\').write(bytes(5*1024*1024))"', work, max_file_mb=1)
    assert r["exit_code"] != 0 and os.path.getsize(os.path.join(work, "big")) <= 1024 * 1024

    # A wall-clock deadline catches a command that sleeps (sleep uses no CPU).
    assert run_limited("sleep 30", work, timeout=1)["exit_code"] == -1

    # Honest limits. The child can still read files outside the workdir and open sockets.
    secret_file = os.path.join(tempfile.mkdtemp(), "outside.txt")
    open(secret_file, "w").write("readable")
    assert run_limited(f"cat {secret_file}", work)["stdout"] == "readable"
    r = run_limited(f'{py} -c "import socket; socket.socket(); print(\'socket ok\')"', work)
    assert r["stdout"].strip() == "socket ok"
    print("ok: limits work; reads and sockets are still open, as the lesson says")
