"""Wait states & persistence: the engine survives its own death.

Extends the Phase-1 token engine with a SQLite store. When a token hits a wait
state, the instance (tokens + variables) is written to the database and the
in-memory object can be thrown away. Completing a task LOADS the instance,
advances it, and saves again — possibly in a different process, days later.

Run: python3 persistent_engine.py
"""
import json
import sqlite3
import uuid
from dataclasses import dataclass

DB = "engine.db"


@dataclass
class Node:
    name: str
    kind: str            # "start" | "end" | "service" | "user"
    handler: object = None


@dataclass
class Process:
    key: str
    nodes: dict
    flows: list

    def next_of(self, name):
        return [t for s, t in self.flows if s == name]


class Engine:
    """One engine instance = one connection to the shared state. Any number of
    Engine objects (processes, nodes) can serve the same instances."""

    def __init__(self, processes, db=DB):
        self.processes = {p.key: p for p in processes}
        self.conn = sqlite3.connect(db)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS instances ("
            " id TEXT PRIMARY KEY, process_key TEXT,"
            " tokens TEXT, variables TEXT)")

    # -- persistence -------------------------------------------------------
    def _save(self, inst_id, key, tokens, variables):
        if tokens:
            self.conn.execute(
                "INSERT OR REPLACE INTO instances VALUES (?,?,?,?)",
                (inst_id, key, json.dumps(tokens), json.dumps(variables)))
        else:   # complete: runtime rows are deleted (history is Phase 9)
            self.conn.execute("DELETE FROM instances WHERE id=?", (inst_id,))
        self.conn.commit()

    def _load(self, inst_id):
        row = self.conn.execute(
            "SELECT process_key, tokens, variables FROM instances WHERE id=?",
            (inst_id,)).fetchone()
        assert row, f"no such instance {inst_id!r} (completed instances vanish)"
        return row[0], json.loads(row[1]), json.loads(row[2])

    # -- the two operations ------------------------------------------------
    def start(self, key, variables=None):
        process = self.processes[key]
        inst_id = uuid.uuid4().hex[:8]
        entry = next(n for n in process.nodes.values() if n.kind == "start")
        tokens, variables = self._advance(process, [entry.name], dict(variables or {}))
        self._save(inst_id, key, tokens, variables)
        return inst_id, tokens

    def complete_task(self, inst_id, task, extra_vars=None):
        key, tokens, variables = self._load(inst_id)          # rehydrate
        process = self.processes[key]
        assert task in tokens, f"no token waiting at {task!r}"
        variables.update(extra_vars or {})
        tokens[tokens.index(task)] = process.next_of(task)[0]
        tokens, variables = self._advance(process, tokens, variables)
        self._save(inst_id, key, tokens, variables)           # sleep again (or finish)
        return tokens

    # -- same advance loop as Phase 1 --------------------------------------
    def _advance(self, process, tokens, variables):
        progressed = True
        while progressed:
            progressed = False
            surviving = []
            for at in tokens:
                node = process.nodes[at]
                if node.kind == "user":
                    surviving.append(at)
                elif node.kind == "end":
                    progressed = True
                else:
                    if node.kind == "service" and node.handler:
                        node.handler(variables)
                    surviving.append(process.next_of(at)[0])
                    progressed = True
            tokens = surviving
        return tokens, variables


LEAVE = Process(
    key="leave",
    nodes={
        "start":   Node("start", "start"),
        "approve": Node("approve", "user"),
        "notify":  Node("notify", "service",
                        handler=lambda v: v.update(notified=True)),
        "done":    Node("done", "end"),
    },
    flows=[("start", "approve"), ("approve", "notify"), ("notify", "done")],
)


if __name__ == "__main__":
    import os
    if os.path.exists(DB):
        os.remove(DB)

    engine_a = Engine([LEAVE])
    inst_id, tokens = engine_a.start("leave", {"employee": "priya"})
    print("started", inst_id, "- sleeping at", tokens)
    del engine_a                       # "server crash": all memory gone

    engine_b = Engine([LEAVE])         # "restart" — state comes from the DB
    tokens = engine_b.complete_task(inst_id, "approve", {"approved": True})
    print("after approval:", tokens or "instance complete")
    left = engine_b.conn.execute("SELECT COUNT(*) FROM instances").fetchone()[0]
    print("runtime rows remaining:", left)
    os.remove(DB)
