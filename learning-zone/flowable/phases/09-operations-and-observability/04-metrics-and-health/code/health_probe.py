"""The engine health probe: the numbers worth waking someone for.

Polls one engine and emits the six signals the dashboard spec defines, with
an ALERT line for each breached threshold. Run it from cron, wrap it in a
Prometheus exporter, or paste its output into the incident channel — the
numbers are the contract, the transport is your choice.

Prereq:  docker run -p 8080:8080 flowable/flowable-rest
Run:     python3 health_probe.py
"""
import base64
import datetime
import json
import urllib.request

BASE = "http://localhost:8080/flowable-rest/service"
AUTH = base64.b64encode(b"rest-admin:test").decode()

THRESHOLDS = {
    "dead_letter_jobs": 0,        # anything > 0 is a silently stuck process
    "overdue_timer_jobs": 10,     # executor not keeping up with due timers
    "oldest_instance_days": 45,   # far beyond the process's designed lifetime
    "deepest_pool": 50,           # staffing vs inflow imbalance
    "overdue_tasks": 25,          # SLA breaches in the making
}


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def total(path, body=None):
    return (call("POST", path, body) if body else call("GET", path)).get("total", 0)


def probe(groups=("credit-ops", "kyc-ops", "applicants")):
    now = datetime.datetime.now(datetime.timezone.utc)
    iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    oldest_days = 0.0
    insts = call("GET", "/runtime/process-instances?sort=startTime&order=asc&size=1"
                 ).get("data", [])
    if insts:
        started = datetime.datetime.fromisoformat(
            insts[0]["startTime"].replace("Z", "+00:00"))
        oldest_days = round((now - started).total_seconds() / 86400, 1)

    pools = {g: total("/query/tasks", {"candidateGroup": g, "unassigned": True})
             for g in groups}

    return {
        "open_instances": total("/runtime/process-instances?size=1"),
        "dead_letter_jobs": total("/management/deadletter-jobs?size=1"),
        "overdue_timer_jobs": total(f"/management/timer-jobs?dueBefore={iso}&size=1"),
        "oldest_instance_days": oldest_days,
        "deepest_pool": max(pools.values(), default=0),
        "pools": pools,
        "overdue_tasks": total("/query/tasks", {"dueBefore": iso}),
    }


if __name__ == "__main__":
    m = probe()
    print(f"open instances        : {m['open_instances']}")
    print(f"dead-letter jobs      : {m['dead_letter_jobs']}")
    print(f"overdue timer jobs    : {m['overdue_timer_jobs']}")
    print(f"oldest instance (days): {m['oldest_instance_days']}")
    print(f"pools                 : {m['pools']}")
    print(f"overdue tasks         : {m['overdue_tasks']}")

    alerts = [k for k, limit in THRESHOLDS.items() if m[k] > limit]
    for k in alerts:
        print(f"ALERT {k} = {m[k]} (threshold {THRESHOLDS[k]})")
    raise SystemExit(1 if alerts else 0)      # cron/CI-friendly exit code
