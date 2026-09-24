"""Forms over REST: read what a task asks for, answer it, complete it.

Uses form PROPERTIES declared in the model (the engine-side contract); the
rendering is yours. Deploy outputs/leave-request-form.bpmn20.xml first (or
run this file — it deploys it for you).

Prereq:  docker run -p 8080:8080 flowable/flowable-rest
Run:     python3 form_client.py
"""
import base64
import json
import pathlib
import urllib.request
import uuid

BASE = "http://localhost:8080/flowable-rest/service"
AUTH = base64.b64encode(b"rest-admin:test").decode()
MODEL = pathlib.Path(__file__).resolve().parents[1] / "outputs" / \
    "leave-request-form.bpmn20.xml"


def call(method, path, body=None, content_type="application/json"):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    if body is not None:
        req.add_header("Content-Type", content_type)
        req.data = body if isinstance(body, bytes) else json.dumps(body).encode()
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def deploy(path):
    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
            f'filename="{path.name}"\r\nContent-Type: application/xml\r\n\r\n'
            ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    call("POST", "/repository/deployments", body,
         content_type=f"multipart/form-data; boundary={boundary}")


def form_of(task_id):
    """The engine-side contract: what this task asks for."""
    return call("GET", f"/form/form-data?taskId={task_id}")


def submit(task_id, answers):
    """Submit THROUGH the form endpoint: the engine enforces the contract
    (types, required, enum values) before completing the task."""
    call("POST", "/form/form-data", {
        "taskId": task_id,
        "properties": [{"id": k, "value": v} for k, v in answers.items()],
    })


if __name__ == "__main__":
    deploy(MODEL)
    call("POST", "/runtime/process-instances",
         {"processDefinitionKey": "leaveRequestForm",
          "variables": [{"name": "employee", "value": "priya"}]})

    task = call("POST", "/query/tasks",
                {"processDefinitionKey": "leaveRequestForm", "size": 1})["data"][0]

    print("the task asks for:")
    for p in form_of(task["id"])["formProperties"]:
        line = f"  {p['id']} ({p['type']}{', required' if p['required'] else ''})"
        if p.get("enumValues"):
            line += " one of " + str([e["id"] for e in p["enumValues"]])
        print(line)

    submit(task["id"], {"approved": "true", "comment": "enjoy the break"})
    print("submitted; task gone:",
          call("POST", "/query/tasks",
               {"processDefinitionKey": "leaveRequestForm"})["total"] == 0)
