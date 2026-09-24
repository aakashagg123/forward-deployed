"""Instance migration: move live tokens from an old definition to the latest.

The three-step ritual, per instance:
  1. VALIDATE the migration server-side (dry run — where would tokens land?)
  2. MIGRATE with explicit activity mappings where element ids changed
  3. VERIFY the instance now reports the target definition

Java's ProcessInstanceMigrationBuilder is the canonical API; this client uses
the REST equivalents so the ritual is scriptable from anywhere.

Prereq:  a running engine with 2+ versions of a key and pinned instances
         (run lesson 01's versions_client.py first)
Run:     python3 migration_client.py loanTriage
"""
import base64
import json
import sys
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


def versions(key):
    return call("GET", f"/repository/process-definitions?key={key}"
                       "&sort=version&order=desc").get("data", [])


def stragglers(key, latest_id):
    """Live instances NOT on the latest definition — the migration backlog."""
    out = []
    for inst in call("GET", f"/runtime/process-instances?processDefinitionKey={key}"
                            "&size=200").get("data", []):
        if inst["processDefinitionId"] != latest_id:
            out.append(inst)
    return out


def migrate(instance_id, target_def_id, mappings=None):
    doc = {"toProcessDefinitionId": target_def_id}
    if mappings:
        # only needed where element ids changed / were replaced:
        # [{"fromActivityId": "approveOld", "toActivityId": "approveNew"}]
        doc["activityMigrationMappings"] = mappings

    call("POST", f"/runtime/process-instances/{instance_id}/migrate/validate", doc)
    call("POST", f"/runtime/process-instances/{instance_id}/migrate", doc)

    moved = call("GET", f"/runtime/process-instances?id={instance_id}")["data"][0]
    assert moved["processDefinitionId"] == target_def_id, "verify failed"
    return moved


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "loanTriage"
    defs = versions(key)
    assert len(defs) >= 2, "need 2+ versions — run versions_client.py first"
    latest = defs[0]["id"]

    backlog = stragglers(key, latest)
    print(f"{len(backlog)} instance(s) not on latest ({latest})")

    ok, failed = 0, []
    for inst in backlog:
        try:
            migrate(inst["id"], latest)
            ok += 1
            print(f"  migrated {inst['id']}  {inst['processDefinitionId']} -> latest")
        except (urllib.error.HTTPError, AssertionError) as e:
            failed.append((inst["id"], str(e)))
            print(f"  SKIPPED  {inst['id']}: {e}  (needs explicit mappings?)")

    print(f"\nmigrated {ok}, failed {len(failed)}, "
          f"remaining stragglers: {len(stragglers(key, latest))}")
