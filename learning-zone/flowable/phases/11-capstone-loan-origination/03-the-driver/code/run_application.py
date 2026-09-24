"""Capstone driver: run one loan application end to end over REST.

Deploys the process + decision table, starts an application, works every
human task in order (KYC, optional manual review, offer acceptance), then
prints the audit timeline. Every helper here was built in an earlier phase —
this file just composes them.

Prereq:  docker run -p 8080:8080 flowable/flowable-rest
         (bureauBaseUrl points at a fake host, so the bureau branch exercises
          the Phase-4 error boundary -> manual score entry, deterministically)
Run:     python3 run_application.py [score] [amount] [employment]
"""
import base64
import json
import pathlib
import sys
import time
import urllib.request
import uuid

BASE = "http://localhost:8080/flowable-rest/service"
AUTH = base64.b64encode(b"rest-admin:test").decode()
HERE = pathlib.Path(__file__).resolve()
BPMN = HERE.parents[2] / "01-process-model" / "outputs" / "loan-origination.bpmn20.xml"
DMN = HERE.parents[2] / "02-credit-decision-table" / "outputs" / "loan-decision.dmn"


def call(method, path, body=None, content_type="application/json", base=BASE):
    req = urllib.request.Request(base + path, method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    if body is not None:
        req.add_header("Content-Type", content_type)
        req.data = body if isinstance(body, bytes) else json.dumps(body).encode()
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def deploy(path, endpoint="/repository/deployments"):
    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
            f'filename="{path.name}"\r\nContent-Type: application/xml\r\n\r\n'
            ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    call("POST", endpoint, body,
         content_type=f"multipart/form-data; boundary={boundary}")
    print(f"deployed {path.name}")


def open_tasks(instance_id, wait_s=15):
    """Poll briefly: the async bureau task + its error boundary need a moment."""
    for _ in range(wait_s * 2):
        tasks = call("GET", f"/runtime/tasks?processInstanceId={instance_id}") \
            .get("data", [])
        if tasks:
            return tasks
        if not call("GET", f"/runtime/process-instances?id={instance_id}")["total"]:
            return []                                  # instance finished
        time.sleep(0.5)
    return []


def complete(task, variables):
    print(f"  completing '{task['name']}' with {variables}")
    call("POST", f"/runtime/tasks/{task['id']}", {
        "action": "complete",
        "variables": [{"name": k, "value": v} for k, v in variables.items()],
    })


def timeline(instance_id):
    acts = call("GET", "/history/historic-activity-instances"
                       f"?processInstanceId={instance_id}&sort=startTime").get("data", [])
    return [a["activityId"] for a in acts if a.get("activityType") != "sequenceFlow"]


if __name__ == "__main__":
    score = int(sys.argv[1]) if len(sys.argv) > 1 else 720
    amount = int(sys.argv[2]) if len(sys.argv) > 2 else 400_000
    employment = sys.argv[3] if len(sys.argv) > 3 else "salaried"

    deploy(DMN, "/dmn-repository/deployments")
    deploy(BPMN)

    app_id = f"APP-{uuid.uuid4().hex[:6].upper()}"
    inst = call("POST", "/runtime/process-instances", {
        "processDefinitionKey": "loanOrigination",
        "businessKey": app_id,                          # Phase 7: correlation-ready
        "variables": [
            {"name": "pan", "value": "ABCDE1234F"},
            {"name": "amount", "value": amount},
            {"name": "employment", "value": employment},
            {"name": "bureauBaseUrl", "value": "http://bureau.invalid"},
            {"name": "offerValidity", "value": "P30D"},
        ],
    })
    print(f"\nstarted {app_id} (instance {inst['id']}): "
          f"score={score} amount={amount:,} {employment}")

    # Work the inbox until the instance finishes. The answers per task type:
    answers = {
        "manualBureauPull": {"score": score},           # bureau.invalid -> boundary fired
        "kycReview":        {"kycOk": True},
        "creditReview":     {"decision": "auto-approve"},
        "acceptOffer":      {"accepted": True},
    }
    while True:
        tasks = open_tasks(inst["id"])
        if not tasks:
            break
        for task in tasks:
            key = task["taskDefinitionKey"]
            complete(task, answers[key])

    print("\naudit timeline:", " -> ".join(timeline(inst["id"])))
    hist = call("GET", "/history/historic-variable-instances"
                       f"?processInstanceId={inst['id']}").get("data", [])
    final = {v["variable"]["name"]: v["variable"]["value"] for v in hist}
    print(f"decision={final.get('decision')} rate={final.get('rate')} "
          f"outcome={final.get('outcome', 'not disbursed')}")
