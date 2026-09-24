"""Drive a real Flowable engine over REST — stdlib only, no SDK.

Prereq:  docker run -p 8080:8080 flowable/flowable-rest
Run:     python3 flowable_client.py

Walks the full lifecycle: deploy the lesson-03 model, start two instances
(one auto-approved, one parked at manual review), complete the review task,
then read the audit trail from history.
"""
import base64
import json
import mimetypes
import pathlib
import urllib.request
import uuid

BASE = "http://localhost:8080/flowable-rest/service"
AUTH = base64.b64encode(b"rest-admin:test").decode()
MODEL = pathlib.Path(__file__).resolve().parents[2] / \
    "03-bpmn-xml-by-hand" / "outputs" / "loan-triage.bpmn20.xml"


def call(method, path, body=None, content_type="application/json"):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    if body is not None:
        req.add_header("Content-Type", content_type)
        req.data = body if isinstance(body, bytes) else json.dumps(body).encode()
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def deploy(bpmn_path):
    """POST the model as multipart/form-data; the engine parses and versions it."""
    boundary = uuid.uuid4().hex
    filename = bpmn_path.name
    ctype = mimetypes.guess_type(filename)[0] or "application/xml"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode() + bpmn_path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    return call("POST", "/repository/deployments", body,
                content_type=f"multipart/form-data; boundary={boundary}")


def start_instance(key, variables):
    return call("POST", "/runtime/process-instances", {
        "processDefinitionKey": key,
        "variables": [{"name": k, "value": v} for k, v in variables.items()],
    })


def open_tasks(instance_id):
    res = call("GET", f"/runtime/tasks?processInstanceId={instance_id}")
    return res.get("data", [])


def complete_task(task_id, variables):
    call("POST", f"/runtime/tasks/{task_id}", {
        "action": "complete",
        "variables": [{"name": k, "value": v} for k, v in variables.items()],
    })


def history(instance_id):
    res = call("GET",
               f"/history/historic-activity-instances?processInstanceId={instance_id}")
    return [a["activityId"] for a in res.get("data", [])]


if __name__ == "__main__":
    dep = deploy(MODEL)
    print("deployed:", dep["id"], dep["name"])

    fast = start_instance("loanTriage", {"applicant": "meera", "score": 720})
    print("score 720 -> ended:", fast["ended"])            # True: straight through

    slow = start_instance("loanTriage", {"applicant": "arjun", "score": 640})
    print("score 640 -> ended:", slow["ended"])            # False: token is waiting
    tasks = open_tasks(slow["id"])
    print("waiting at:", [(t["name"], t["id"]) for t in tasks])

    complete_task(tasks[0]["id"], {"decision": "manually-approved"})
    print("after review -> open tasks:", open_tasks(slow["id"]))

    print("audit trail:", history(slow["id"]))
