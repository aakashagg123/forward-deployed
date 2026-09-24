"""Definition versions: what a redeploy actually does — observed, not assumed.

Deploys the same process key twice, starts an instance under each, and shows
the engine's three version rules in the output:
  1. redeploying a key creates version N+1 (old versions stay);
  2. new starts bind to the LATEST version at start time;
  3. running instances keep the version they started on, forever.

Prereq:  docker run -p 8080:8080 flowable/flowable-rest
Run:     python3 versions_client.py
"""
import base64
import json
import pathlib
import urllib.request
import uuid

BASE = "http://localhost:8080/flowable-rest/service"
AUTH = base64.b64encode(b"rest-admin:test").decode()
MODEL = pathlib.Path(__file__).resolve().parents[3] / \
    "01-bpmn-and-the-token-model" / "03-bpmn-xml-by-hand" / "outputs" / \
    "loan-triage.bpmn20.xml"


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


def versions(key):
    data = call("GET", f"/repository/process-definitions?key={key}"
                       "&sort=version&order=desc").get("data", [])
    return [(d["version"], d["id"]) for d in data]


def start_parked(key):
    """Low score -> parks at manual review, so the instance stays alive."""
    return call("POST", "/runtime/process-instances", {
        "processDefinitionKey": key,
        "variables": [{"name": "score", "value": 600}],
    })


if __name__ == "__main__":
    deploy(MODEL)
    print("after 1st deploy:", versions("loanTriage"))

    inst_v_old = start_parked("loanTriage")
    old_def = inst_v_old["processDefinitionId"]

    deploy(MODEL)                                   # same file, same key -> new version
    print("after 2nd deploy:", versions("loanTriage"))

    inst_v_new = start_parked("loanTriage")
    latest_def = versions("loanTriage")[0][1]

    print("\nnew start binds latest :", inst_v_new["processDefinitionId"] == latest_def)
    still = call("GET", f"/runtime/process-instances?id={inst_v_old['id']}")["data"][0]
    print("old instance still pinned:", still["processDefinitionId"] == old_def)
    print("\n-> two live instances of one key, on two definitions. Moving the",
          "old one is MIGRATION (lesson 02); until then both versions execute.")
