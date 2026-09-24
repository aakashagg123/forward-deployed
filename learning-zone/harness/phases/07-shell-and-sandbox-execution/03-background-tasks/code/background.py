"""A background-job manager: start / output / status / stop. Run: python3 background.py"""
import os
import signal
import subprocess
import tempfile


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


if __name__ == "__main__":
    import time
    jobs = BackgroundJobs()
    h = jobs.start("for i in 1 2 3; do echo line $i; sleep 0.1; done")
    time.sleep(0.5)
    print(jobs.status(h["id"]), "|", jobs.output(h["id"]).split())
    print(jobs.stop(h["id"]))
