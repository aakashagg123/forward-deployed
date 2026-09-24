"""Run a command with a deadline; kill the process group on expiry.

Run:  python3 timeout_run.py
"""
import os
import signal
import subprocess


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


if __name__ == "__main__":
    print(run("echo quick", timeout=5))
    print(run("sleep 30", timeout=1))
