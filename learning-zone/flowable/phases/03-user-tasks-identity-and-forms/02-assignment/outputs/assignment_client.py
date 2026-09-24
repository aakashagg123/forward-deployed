"""Assignment over REST: candidate groups, the claim race, and completion.

Deploys nothing new — uses Phase 1's loanTriage model (deploy it first with
Phase 1's client). Shows the worklist protocol end to end:

  list group tasks -> claim (watch the loser get 409'd) -> complete

Prereq:  docker run -p 8080:8080 flowable/flowable-rest
Run:     python3 assignment_client.py
"""
import base64
import json
import urllib.error
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


def group_pool(group):
    """The unclaimed pool for a group: candidate tasks with no assignee yet."""
    return call("POST", "/query/tasks", {
        "candidateGroup": group, "unassigned": True, "size": 50,
    }).get("data", [])


def my_tasks(user):
    return call("POST", "/query/tasks", {"assignee": user, "size": 50}).get("data", [])


def claim(task_id, user):
    call("POST", f"/runtime/tasks/{task_id}", {"action": "claim", "assignee": user})


def complete(task_id, variables=None):
    call("POST", f"/runtime/tasks/{task_id}", {
        "action": "complete",
        "variables": [{"name": k, "value": v} for k, v in (variables or {}).items()],
    })


if __name__ == "__main__":
    # A low score parks an instance at 'Manual credit review' (candidate
    # group credit-ops — see loan-triage.bpmn20.xml).
    inst = call("POST", "/runtime/process-instances", {
        "processDefinitionKey": "loanTriage",
        "variables": [{"name": "score", "value": 640},
                      {"name": "applicant", "value": "arjun"}],
    })

    pool = group_pool("credit-ops")
    print(f"credit-ops pool: {[(t['name'], t['id']) for t in pool]}")
    task = pool[0]

    claim(task["id"], "asha")
    print("asha claimed", task["id"])

    try:
        claim(task["id"], "ravi")                 # the race's loser
    except urllib.error.HTTPError as e:
        print(f"ravi refused: HTTP {e.code} (already claimed)")

    print("asha's list :", [t["id"] for t in my_tasks("asha")])
    print("pool now    :", group_pool("credit-ops"))   # empty: claimed tasks leave it

    complete(task["id"], {"decision": "approved"})
    print("completed; instance ended:",
          call("GET", f"/runtime/process-instances?id={inst['id']}")["total"] == 0)
