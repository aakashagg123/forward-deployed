# ---
# name: token-engine
# description: Minimal token-based process engine — the reusable core later lessons extend
# kind: module
# phase: 01
# lesson: 01
# ---
"""Reusable core of the toy process engine (see ../code/token_engine.py for the
narrated version with a runnable demo)."""
from dataclasses import dataclass, field


@dataclass
class Node:
    name: str
    kind: str            # "start" | "end" | "service" | "user"
    handler: object = None


@dataclass
class Process:
    nodes: dict
    flows: list

    def next_of(self, name):
        return [t for s, t in self.flows if s == name]


@dataclass
class Instance:
    process: Process
    tokens: list = field(default_factory=list)
    variables: dict = field(default_factory=dict)
    log: list = field(default_factory=list)

    @property
    def complete(self):
        return not self.tokens


def start(process, variables=None):
    inst = Instance(process, variables=dict(variables or {}))
    entry = next(n for n in process.nodes.values() if n.kind == "start")
    inst.tokens = [entry.name]
    advance(inst)
    return inst


def advance(inst):
    progressed = True
    while progressed:
        progressed = False
        surviving = []
        for at in inst.tokens:
            node = inst.process.nodes[at]
            if node.kind == "user":
                surviving.append(at)
            elif node.kind == "end":
                inst.log.append(f"end reached: {at}")
                progressed = True
            else:
                if node.kind == "service" and node.handler:
                    node.handler(inst.variables)
                inst.log.append(f"executed: {at}")
                targets = inst.process.next_of(at)
                assert len(targets) == 1, f"{at}: multiple flows need a gateway"
                surviving.append(targets[0])
                progressed = True
        inst.tokens = surviving


def complete_user_task(inst, name, variables=None):
    assert name in inst.tokens, f"no token waiting at {name!r}"
    inst.variables.update(variables or {})
    inst.log.append(f"completed: {name}")
    inst.tokens[inst.tokens.index(name)] = inst.process.next_of(name)[0]
    advance(inst)
