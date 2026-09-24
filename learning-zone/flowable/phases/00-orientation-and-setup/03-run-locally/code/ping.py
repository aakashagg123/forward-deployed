"""First contact: is the engine up, what's deployed, can I talk to it?

The three checks every Flowable session starts with, as one script — run it
whenever a lesson's Use It "doesn't work" before debugging anything else.

Prereq:  docker run -p 8080:8080 flowable/flowable-rest
Run:     python3 ping.py
"""
import base64
import json
import urllib.error
import urllib.request

BASE = "http://localhost:8080/flowable-rest/service"
AUTH = base64.b64encode(b"rest-admin:test").decode()


def call(path):
    req = urllib.request.Request(BASE + path)
    req.add_header("Authorization", f"Basic {AUTH}")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    # 1. Reachability + auth (the two failure modes look identical from a UI)
    try:
        engine = call("/management/engine")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"reached the engine but auth failed: HTTP {e.code} "
                         "(default credentials are rest-admin/test)")
    except urllib.error.URLError as e:
        raise SystemExit(f"engine unreachable at {BASE}: {e.reason}\n"
                         "-> docker run -p 8080:8080 flowable/flowable-rest")
    print(f"engine  : {engine['name']} {engine['version']}")

    # 2. What's deployed? (empty on a fresh container — that's correct)
    defs = call("/repository/process-definitions?latest=true&size=50")
    print(f"deployed: {defs['total']} process definition(s)")
    for d in defs.get("data", []):
        print(f"  - {d['key']} v{d['version']}")

    # 3. Anything alive? (fresh container: zeros across the board)
    for label, path in [("open instances ", "/runtime/process-instances?size=1"),
                        ("open tasks     ", "/runtime/tasks?size=1"),
                        ("dead letters   ", "/management/deadletter-jobs?size=1")]:
        print(f"{label}: {call(path)['total']}")

    print("\nengine is ready — next: deploy something "
          "(Phase 1, lesson 04's flowable_client.py)")
