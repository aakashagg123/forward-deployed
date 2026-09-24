"""Bounded roles: build each agent's context from an explicit allowlist.

Enforcement is structural — a role's prompt is constructed only from keys it is
allowed to see. assert_no_leak is a contract test you can run in CI.

Run:  python3 roles.py
"""

ROLE_ALLOWLIST = {
    "planner": ["spec"],
    "worker": ["contract", "files"],
    "reviewer": ["diff"],                          # never "plan" or "spec"
    "memory": ["review_report"],
}


def build_context(role, store):
    """Return only the store entries this role is allowed to read."""
    allowed = ROLE_ALLOWLIST[role]
    return {k: store[k] for k in allowed if k in store}


def assert_no_leak(role, ctx):
    forbidden = set(ctx) - set(ROLE_ALLOWLIST[role])
    if forbidden:
        raise AssertionError(f"{role} context leaked: {forbidden}")
    return ctx


if __name__ == "__main__":
    store = {"spec": "...", "plan": "...", "diff": "- old\n+ new", "review_report": "..."}

    reviewer_ctx = build_context("reviewer", store)
    print("reviewer sees:", list(reviewer_ctx))    # ['diff'] — plan/spec absent
    assert_no_leak("reviewer", reviewer_ctx)

    worker_ctx = build_context("worker", store)
    print("worker sees:  ", list(worker_ctx))      # [] here (no contract/files in store)
    print("no leaks detected")
