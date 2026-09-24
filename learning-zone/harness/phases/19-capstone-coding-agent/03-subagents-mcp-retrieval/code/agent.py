"""Capstone 03: supervisor + subagents (P10) + retrieval (P13) + MCP tools (P12).

Self-contained; stubs for subagent/search. Run:  python3 agent.py
"""


def decompose(goal):
    return [{"text": p.strip()} for p in goal.split(" and ") if p.strip()]


def chunked(items, n):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def aggregate(results):
    ok = [r for r in results if r["ok"]]
    return {"completed": [r["task"] for r in ok],
            "summary": f"{len(ok)}/{len(results)} subagents succeeded"}


def supervise(goal, run_subagent, search_code, max_workers=3):
    tasks = decompose(goal)                       # P10
    for t in tasks:
        t["context"] = search_code(t["text"])     # P13 — locate relevant code first
    results = []
    for batch in chunked(tasks, max_workers):     # bounded parallelism
        results += [run_subagent(t) for t in batch]
    return aggregate(results)


if __name__ == "__main__":
    print(supervise(
        "add a /health route and test the /health route",
        run_subagent=lambda t: {"task": t["text"], "ok": True, "ctx": t["context"]},
        search_code=lambda q: "routes.py:1"))
