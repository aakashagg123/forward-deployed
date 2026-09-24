"""The task inbox pattern: two queries, merged, sorted by urgency.

Every worklist UI ever built on a process engine is this file with pixels:
  my tasks       assignee = me                     (I claimed these — finish them)
  group tasks    candidateGroup in my groups,      (unclaimed pool — take one)
                 unassigned
ordered by due date, overdue flagged. Nothing else is needed for v1.

Prereq:  docker run -p 8080:8080 flowable/flowable-rest  (+ some open tasks)
Run:     python3 inbox_client.py asha credit-ops,mumbai-ops
"""
import base64
import datetime
import json
import sys
import urllib.request

BASE = "http://localhost:8080/flowable-rest/service"
AUTH = base64.b64encode(b"rest-admin:test").decode()


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def query(body):
    body.update({"size": 100, "order": "asc", "sort": "dueDate"})
    return call("POST", "/query/tasks", body).get("data", [])


def inbox(user, groups):
    mine = query({"assignee": user})
    pool = [t for g in groups for t in query({"candidateGroup": g, "unassigned": True})]
    seen, merged = set(), []                    # de-dupe across shared groups
    for t in mine + pool:
        if t["id"] not in seen:
            seen.add(t["id"])
            merged.append(t)
    return mine, merged[len(mine):]


def fmt(task, now):
    due = task.get("dueDate")
    if not due:
        flag = "        "
    else:
        overdue = due[:19] < now
        flag = "OVERDUE " if overdue else f"due {due[5:10]} "
    key = task.get("processInstanceId", "?")
    return f"  [{flag}] {task['name']}  (task {task['id']}, instance {key})"


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "asha"
    groups = (sys.argv[2] if len(sys.argv) > 2 else "credit-ops").split(",")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    mine, pool = inbox(user, groups)
    print(f"== {user}: my tasks ({len(mine)}) — finish these first")
    for t in mine:
        print(fmt(t, now))
    print(f"== pool for {groups} ({len(pool)}) — claim to take one")
    for t in pool:
        print(fmt(t, now))
