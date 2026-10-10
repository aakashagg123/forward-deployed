"""A small coding agent: loop, tools, permission gate, clipped output, todo list, step budget.

A scripted model stands in for the real one, so everything runs offline.
Run the test:  python3 code/test_agent.py
"""
import json
import pathlib
import re
import shlex
import subprocess

# ---- Tools: three that touch the repo, one for the plan. Phase 02 and 05. ----------------
TOOL_SPECS = [
    {"name": "read", "description": "Read a text file inside the repo.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "edit", "description": "Replace one exact string in a file. old must match exactly once.",
     "input_schema": {"type": "object", "required": ["path", "old", "new"],
                      "properties": {"path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}}}},
    {"name": "bash", "description": "Run one command in the repo root. No shell: pipes and && do not work.",
     "input_schema": {"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]}},
    {"name": "todo", "description": "Replace the whole todo list. Status: pending, in_progress, or done.",
     "input_schema": {"type": "object", "required": ["items"], "properties": {"items": {"type": "array", "items": {
         "type": "object", "required": ["text", "status"],
         "properties": {"text": {"type": "string"}, "status": {"type": "string"}}}}}}},
]

# ---- Permission gate. Phase 06: deny first, then ask, then allow; the default is ask. ----
RULES = [
    ("deny", "bash", r"\b(rm|sudo|curl|wget)\b|git push"),
    ("ask", "edit", r".*"),
    ("allow", "bash", r"^python3 -m unittest( -v)?( \S+)?$"),
    ("allow", "read", r".*"),
    ("allow", "todo", r".*"),
]


def decide(name, args):
    text = args.get("cmd") or args.get("path") or ""
    for verdict in ("deny", "ask", "allow"):
        if any(v == verdict and t == name and re.search(p, text) for v, t, p in RULES):
            return verdict
    return "ask"


# ---- Output limits. Phase 03: clip one result, then drop old turns in whole pairs. -------
def clip(text, limit=2000):
    if len(text) <= limit:
        return text
    half = limit // 2
    return text[:half] + f"\n[... {len(text) - 2 * half} chars cut ...]\n" + text[-half:]


def trim_history(history, limit):
    """Drop the oldest (assistant, tool_result) pairs. A tool_use never loses its tool_result."""
    def size(msgs):
        return sum(len(json.dumps(m)) for m in msgs)

    head, rest, dropped = history[0], history[1:], 0
    while size([head] + rest) > limit and len(rest) > 2:
        rest, dropped = rest[2:], dropped + 1
    if dropped:
        head = {"role": "user", "content": f"{head['content']}\n[{dropped} earlier steps trimmed]"}
    return [head] + rest


# ---- The agent. Phase 01: a loop that calls the model, runs tools, feeds results back. ----
class Agent:
    def __init__(self, root, model, approve=lambda name, args: False, max_steps=12, max_chars=20_000):
        self.root, self.model, self.approve = pathlib.Path(root).resolve(), model, approve
        self.max_steps, self.max_chars, self.todos = max_steps, max_chars, []
        self.tools = {"read": self.read, "edit": self.edit, "bash": self.bash, "todo": self.todo}

    def path(self, rel):
        p = (self.root / rel).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError(f"path outside the repo: {rel}")
        return p

    def read(self, path):
        return self.path(path).read_text()

    def edit(self, path, old, new):
        p = self.path(path)
        text = p.read_text()
        if text.count(old) != 1:
            return f"error: {text.count(old)} matches for old; it must match exactly once"
        p.write_text(text.replace(old, new))
        return "ok: edited"

    def bash(self, cmd):
        r = subprocess.run(shlex.split(cmd), cwd=self.root, capture_output=True, text=True, timeout=30)
        return f"exit {r.returncode}\n{r.stdout}{r.stderr}"

    def todo(self, items):
        self.todos = items
        return "\n".join(f"[{'x' if i['status'] == 'done' else ' '}] {i['text']}" for i in items)

    def call_tool(self, name, args):
        verdict = decide(name, args)
        if verdict == "ask" and self.approve(name, args):
            verdict = "allow"
        if verdict != "allow":
            return f"denied: the permission gate blocked {name} {args}", True
        try:
            return clip(str(self.tools[name](**args))), False
        except Exception as e:                      # errors go back to the model as data
            return f"error: {e}", True

    def run(self, task):
        history = [{"role": "user", "content": task}]
        for step in range(1, self.max_steps + 1):
            blocks = self.model(trim_history(history, self.max_chars))
            history.append({"role": "assistant", "content": blocks})
            uses = [b for b in blocks if b["type"] == "tool_use"]
            if not uses:
                text = "".join(b.get("text", "") for b in blocks)
                return {"status": "done", "steps": step, "text": text, "history": history}
            results = []
            for u in uses:
                out, is_error = self.call_tool(u["name"], u["input"])
                results.append({"type": "tool_result", "tool_use_id": u["id"], "content": out, "is_error": is_error})
            history.append({"role": "user", "content": results})
        return {"status": "budget", "steps": self.max_steps, "text": "", "history": history}


# ---- A scripted model: reads the history, picks the next call. No API key needed. --------
def scripted_model(history):
    uses = [b["name"] for m in history if m["role"] == "assistant" for b in m["content"] if b["type"] == "tool_use"]
    last = history[-1]["content"][0]["content"] if len(history) > 1 else ""

    def use(name, **inp):
        return [{"type": "tool_use", "id": f"toolu_{len(uses)}", "name": name, "input": inp}]

    plan = [{"text": "read calc.py", "status": "done"}, {"text": "fix add()", "status": "pending"},
            {"text": "run the tests", "status": "pending"}]
    if not uses:
        return use("todo", items=plan)
    if uses[-1] == "todo" and "read" not in uses:
        return use("read", path="calc.py")
    if uses[-1] == "read":
        return use("bash", cmd="rm -rf .")                        # a bad idea: the gate must stop it
    if uses[-1] == "bash" and "denied" in last:
        return use("edit", path="calc.py", old="a - b", new="a + b")
    if uses[-1] == "edit":
        return use("bash", cmd="python3 -m unittest")
    if uses[-1] == "bash" and "OK" in last:
        return use("todo", items=[{**i, "status": "done"} for i in plan])
    return [{"type": "text", "text": "Fixed add() and the tests pass."}]
