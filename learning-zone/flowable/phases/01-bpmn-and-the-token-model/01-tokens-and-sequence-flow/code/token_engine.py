"""A process engine in ~100 lines: nodes, sequence flows, tokens.

Node kinds:
  start    - where the token is born
  end      - where a token is consumed
  service  - automatic work; the engine calls handler(variables) and moves on
  user     - a WAIT STATE; the token sleeps until someone completes the task

Run: python3 token_engine.py
"""
from dataclasses import dataclass, field


@dataclass
class Node:
    name: str
    kind: str            # "start" | "end" | "service" | "user"
    handler: object = None


@dataclass
class Process:
    nodes: dict          # name -> Node
    flows: list          # (source, target) sequence flows

    def next_of(self, name):
        return [t for s, t in self.flows if s == name]


@dataclass
class Instance:
    process: Process
    tokens: list = field(default_factory=list)      # node names where tokens sit
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
    """Move every token forward until it reaches a wait state or is consumed."""
    progressed = True
    while progressed:
        progressed = False
        surviving = []
        for at in inst.tokens:
            node = inst.process.nodes[at]
            if node.kind == "user":
                surviving.append(at)                 # wait state: token sleeps
            elif node.kind == "end":
                inst.log.append(f"end reached: {at}")
                progressed = True                    # token consumed
            else:
                if node.kind == "service" and node.handler:
                    node.handler(inst.variables)
                inst.log.append(f"executed: {at}")
                targets = inst.process.next_of(at)
                assert len(targets) == 1, f"{at}: multiple flows need a gateway (lesson 02)"
                surviving.append(targets[0])
                progressed = True
        inst.tokens = surviving


def complete_user_task(inst, name, variables=None):
    """A human finished the task: wake the token and let it run on."""
    assert name in inst.tokens, f"no token waiting at {name!r}"
    inst.variables.update(variables or {})
    inst.log.append(f"completed: {name}")
    inst.tokens[inst.tokens.index(name)] = inst.process.next_of(name)[0]
    advance(inst)


if __name__ == "__main__":
    leave_request = Process(
        nodes={
            "start":   Node("start", "start"),
            "record":  Node("record", "service",
                            handler=lambda v: v.update(recorded=True)),
            "approve": Node("approve", "user"),
            "notify":  Node("notify", "service",
                            handler=lambda v: print(f"  notify: approved={v['approved']}")),
            "done":    Node("done", "end"),
        },
        flows=[("start", "record"), ("record", "approve"),
               ("approve", "notify"), ("notify", "done")],
    )

    inst = start(leave_request, {"employee": "priya", "days": 3})
    print("tokens after start:", inst.tokens)        # ['approve'] — engine sleeps
    assert not inst.complete

    complete_user_task(inst, "approve", {"approved": True})
    print("tokens after approval:", inst.tokens)     # [] — instance complete
    assert inst.complete
    print("log:", *inst.log, sep="\n  ")
