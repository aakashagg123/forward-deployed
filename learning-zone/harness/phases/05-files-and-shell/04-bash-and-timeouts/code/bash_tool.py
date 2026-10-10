"""A bash tool: stdout, stderr, exit code, a deadline, bounded output.

Run:  python3 code/bash_tool.py
"""
import os
import signal
import subprocess
import tempfile
import time


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


def _alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"   # a zombie is already dead
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    # All three signals are captured.
    r = run("echo hello && echo oops 1>&2; exit 3")
    assert (r["stdout"], r["stderr"], r["exit_code"]) == ("hello\n", "oops\n", 3)
    assert format_result(r).startswith("exit=3\nhello")

    # Failure is visible even when stdout looks fine.
    assert run("echo fine; false")["exit_code"] == 1

    # Waiting for input gets EOF, so it cannot hang the loop.
    t0 = time.time()
    assert run("cat", timeout=5)["exit_code"] == 0 and time.time() - t0 < 3

    # A deadline kills the command and its children.
    pidfile = os.path.join(tempfile.mkdtemp(), "child.pid")
    t0 = time.time()
    r = run(f"sleep 30 & echo $! > {pidfile}; wait", timeout=1)
    assert r["timed_out"] and time.time() - t0 < 5
    child = int(open(pidfile).read())
    time.sleep(0.2)
    assert not _alive(child), "child survived the kill"
    assert format_result(r).startswith("TIMEOUT")

    # Long output keeps the head and the tail, and says what it cut.
    big = format_result(run("seq 1 5000"), max_chars=100)
    assert "1\n2\n3" in big and big.rstrip().endswith("5000") and "chars cut" in big
    print(format_result(run("echo done")))
