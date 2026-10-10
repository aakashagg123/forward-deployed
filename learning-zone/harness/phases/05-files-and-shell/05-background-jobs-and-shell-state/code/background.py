"""A background-job manager: start / output / status / wait_for / stop.

Run:  python3 code/background.py
"""
import os
import re
import signal
import subprocess
import tempfile
import time


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


if __name__ == "__main__":
    jobs = BackgroundJobs()
    t0 = time.time()
    h = jobs.start("echo booting; sleep 0.3; echo Listening on 8080; sleep 30")
    assert time.time() - t0 < 1, "start must not block"
    assert jobs.status(h["id"]) == "running"

    # The agent keeps working, then waits for the ready line.
    assert jobs.wait_for(h["id"], r"Listening on \d+", timeout=5)
    assert "booting" in jobs.output(h["id"])
    assert jobs.wait_for(h["id"], r"never appears", timeout=0.3) is False

    # Stop ends the whole process group.
    assert jobs.stop(h["id"]).startswith("exited(")
    assert jobs.status(h["id"]) != "running"

    # A job that fails on its own shows up in status.
    h2 = jobs.start("echo boom 1>&2; exit 7")
    jobs.wait_for(h2["id"], "boom", timeout=2)
    time.sleep(0.2)
    assert jobs.status(h2["id"]) == "exited(7)" and "boom" in jobs.output(h2["id"])
    print("ok:", jobs.status(h["id"]), jobs.status(h2["id"]))
