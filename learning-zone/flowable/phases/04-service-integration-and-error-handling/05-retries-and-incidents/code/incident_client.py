"""Incident triage for a Flowable engine: find, diagnose, and revive failed jobs.

The job executor (Phase 2, lesson 04) retries a failing async task, then files
it in the dead-letter table where NOTHING runs it again. This client is the ops
loop for that table: list dead letters, pull each one's stack trace, group by
failure, and move jobs back for re-execution once the cause is fixed.

Prereq:  docker run -p 8080:8080 flowable/flowable-rest
Run:     python3 incident_client.py            (triage report)
         python3 incident_client.py retry-all  (move every dead letter back)
"""
import base64
import json
import sys
import urllib.request

BASE = "http://localhost:8080/flowable-rest/service"
AUTH = base64.b64encode(b"rest-admin:test").decode()


def call(method, path, body=None, raw=False):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
        return data.decode() if raw else (json.loads(data) if data else {})


def dead_letters():
    return call("GET", "/management/deadletter-jobs?size=100").get("data", [])


def stacktrace(job_id):
    try:
        return call("GET",
                    f"/management/deadletter-jobs/{job_id}/exception-stacktrace",
                    raw=True)
    except urllib.error.HTTPError:
        return ""


def first_line(trace):
    return trace.strip().splitlines()[0] if trace.strip() else "(no stacktrace)"


def revive(job_id):
    """Move the job back to the executable table; the executor picks it up
    with a fresh retry budget. Only do this AFTER fixing the cause."""
    call("POST", f"/management/deadletter-jobs/{job_id}", {"action": "move"})


def triage():
    jobs = dead_letters()
    if not jobs:
        print("dead-letter table is empty — nothing is silently stuck")
        return
    by_cause = {}
    for job in jobs:
        cause = first_line(stacktrace(job["id"]))
        by_cause.setdefault(cause, []).append(job)
    print(f"{len(jobs)} dead-letter job(s), {len(by_cause)} distinct cause(s):\n")
    for cause, group in sorted(by_cause.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(group):3d} x {cause}")
        sample = group[0]
        print(f"        e.g. job {sample['id']}  instance {sample.get('processInstanceId')}"
              f"  element {sample.get('elementId')}\n")
    print("fix the cause, then revive with: python3 incident_client.py retry-all")


def retry_all():
    jobs = dead_letters()
    for job in jobs:
        revive(job["id"])
        print(f"revived job {job['id']} ({job.get('elementId')})")
    print(f"moved {len(jobs)} job(s) back to the executable queue")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "retry-all":
        retry_all()
    else:
        triage()
