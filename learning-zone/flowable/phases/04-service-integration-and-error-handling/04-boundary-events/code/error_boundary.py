"""Error boundary events: teach the token engine to catch business failures.

Two failure planes (lesson 03):
  - BpmnError  -> if a boundary for its code is attached to the failing node,
                  the token MOVES along the boundary's flow (state advances).
  - Exception  -> technical: the advance aborts and the instance records an
                  incident (real engines roll back + retry; Phase 2).

Run: python3 error_boundary.py
"""
from dataclasses import dataclass, field


class BpmnError(Exception):
    """A business outcome off the happy path — carries a code the model routes on."""
    def __init__(self, code, message=""):
        super().__init__(message or code)
        self.code = code


@dataclass
class Node:
    name: str
    kind: str            # "start" | "end" | "service" | "user"
    handler: object = None


@dataclass
class Process:
    nodes: dict
    flows: list                          # (source, target)
    boundaries: dict = field(default_factory=dict)
    # boundaries: activity name -> {error_code: target, ..., None: catch_all_target}

    def next_of(self, name):
        return [t for s, t in self.flows if s == name]

    def catcher_for(self, activity, code):
        table = self.boundaries.get(activity, {})
        return table.get(code, table.get(None))      # named code first, then catch-all


@dataclass
class Instance:
    process: Process
    tokens: list = field(default_factory=list)
    variables: dict = field(default_factory=dict)
    log: list = field(default_factory=list)
    incident: str = None                 # set on technical failure

    @property
    def complete(self):
        return not self.tokens and self.incident is None


def start(process, variables=None):
    inst = Instance(process, variables=dict(variables or {}))
    entry = next(n for n in process.nodes.values() if n.kind == "start")
    inst.tokens = [entry.name]
    advance(inst)
    return inst


def advance(inst):
    progressed = True
    while progressed and inst.incident is None:
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
                target = execute(inst, node)
                if target is None:                    # technical incident: freeze
                    surviving.append(at)
                else:
                    surviving.append(target)
                    progressed = True
        inst.tokens = surviving


def execute(inst, node):
    """Run one automatic node; return the token's next position (or None on incident)."""
    try:
        if node.kind == "service" and node.handler:
            node.handler(inst.variables)
    except BpmnError as e:                            # business plane: route it
        catcher = inst.process.catcher_for(node.name, e.code)
        if catcher is None:
            inst.incident = f"uncaught BpmnError {e.code} at {node.name} (modelling bug)"
            inst.log.append(inst.incident)
            return None
        inst.log.append(f"error {e.code} at {node.name} -> boundary -> {catcher}")
        inst.variables["errorCode"] = e.code
        return catcher
    except Exception as e:                            # technical plane: don't route
        inst.incident = f"technical failure at {node.name}: {e}"
        inst.log.append(inst.incident + " (real engine: rollback + job retry)")
        return None
    inst.log.append(f"executed: {node.name}")
    return inst.process.next_of(node.name)[0]


def complete_user_task(inst, name, variables=None):
    assert name in inst.tokens, f"no token waiting at {name!r}"
    inst.variables.update(variables or {})
    inst.log.append(f"completed: {name}")
    inst.tokens[inst.tokens.index(name)] = inst.process.next_of(name)[0]
    advance(inst)


def make_disbursal(bureau):
    """start -> bureau call -> post payment -> end, with an error boundary on the call."""
    return Process(
        nodes={
            "start":   Node("start", "start"),
            "bureau":  Node("bureau", "service", handler=bureau),
            "pay":     Node("pay", "service",
                            handler=lambda v: v.update(paid=True)),
            "manual":  Node("manual", "user"),        # boundary target: human pulls report
            "done":    Node("done", "end"),
            "doneM":   Node("doneM", "end"),
        },
        flows=[("start", "bureau"), ("bureau", "pay"), ("pay", "done"),
               ("manual", "doneM")],
        boundaries={"bureau": {"NO_BUREAU_RECORD": "manual"}},
    )


if __name__ == "__main__":
    ok = start(make_disbursal(lambda v: v.update(score=720)))
    print("happy path  ->", "complete" if ok.complete else ok.tokens)

    def no_record(v):
        raise BpmnError("NO_BUREAU_RECORD", "PAN has no bureau file")
    routed = start(make_disbursal(no_record))
    print("BpmnError   -> waiting at", routed.tokens, "| errorCode =",
          routed.variables["errorCode"])
    complete_user_task(routed, "manual", {"score": 680})
    assert routed.complete

    def bureau_down(v):
        raise TimeoutError("bureau timed out")
    frozen = start(make_disbursal(bureau_down))
    print("technical   -> incident:", frozen.incident)
    assert not frozen.complete and frozen.tokens == ["bureau"]

    def weird(v):
        raise BpmnError("LIMIT_EXCEEDED")             # no catcher for this code
    hole = start(make_disbursal(weird))
    print("uncaught    -> incident:", hole.incident)
