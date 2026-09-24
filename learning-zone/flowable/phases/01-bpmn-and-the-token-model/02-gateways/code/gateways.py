"""Gateways: teach the token engine to choose (exclusive) and to fork/join (parallel).

Flows grow a guard: (source, target, guard) where guard is fn(variables) -> bool
or None (unconditional / default flow).

Run: python3 gateways.py
"""
from dataclasses import dataclass, field


@dataclass
class Node:
    name: str
    kind: str            # "start" | "end" | "service" | "user" | "exclusive" | "parallel"
    handler: object = None


@dataclass
class Process:
    nodes: dict
    flows: list          # (source, target, guard)

    def outgoing(self, name):
        return [(t, g) for s, t, g in self.flows if s == name]

    def incoming_count(self, name):
        return sum(1 for _, t, _ in self.flows if t == name)


@dataclass
class Instance:
    process: Process
    tokens: list = field(default_factory=list)
    variables: dict = field(default_factory=dict)
    log: list = field(default_factory=list)

    @property
    def complete(self):
        return not self.tokens


def take_exclusive(inst, node):
    """Exactly one way out: first flow whose guard passes; guardless flow = default."""
    conditional = [(t, g) for t, g in inst.process.outgoing(node.name) if g]
    default = [t for t, g in inst.process.outgoing(node.name) if g is None]
    for target, guard in conditional:
        if guard(inst.variables):
            return [target]
    assert default, f"{node.name}: no condition matched and no default flow"
    return [default[0]]


def take_parallel(inst, node):
    """Fork: token per outgoing flow. Join: wait until all incoming tokens arrive."""
    arrived = inst.tokens.count(node.name)
    if arrived < inst.process.incoming_count(node.name):
        return None                                   # join still waiting
    for _ in range(arrived - 1):                      # merge: n tokens become 1
        inst.tokens.remove(node.name)
    return [t for t, _ in inst.process.outgoing(node.name)]


def advance(inst):
    progressed = True
    while progressed:
        progressed = False
        for at in list(dict.fromkeys(inst.tokens)):   # each position once per sweep
            node = inst.process.nodes[at]
            if node.kind == "user":
                continue
            if node.kind == "end":
                inst.tokens.remove(at)
                inst.log.append(f"end reached: {at}")
                progressed = True
                continue
            if node.kind == "exclusive":
                targets = take_exclusive(inst, node)
            elif node.kind == "parallel":
                targets = take_parallel(inst, node)
                if targets is None:
                    continue                          # not all branches arrived yet
            else:
                if node.kind == "service" and node.handler:
                    node.handler(inst.variables)
                targets = [t for t, _ in inst.process.outgoing(at)]
                assert len(targets) == 1, f"{at}: multiple flows need a gateway"
            inst.log.append(f"executed: {at} -> {targets}")
            inst.tokens.remove(at)
            inst.tokens.extend(targets)
            progressed = True


def start(process, variables=None):
    inst = Instance(process, variables=dict(variables or {}))
    entry = next(n for n in process.nodes.values() if n.kind == "start")
    inst.tokens = [entry.name]
    advance(inst)
    return inst


def complete_user_task(inst, name, variables=None):
    assert name in inst.tokens, f"no token waiting at {name!r}"
    inst.variables.update(variables or {})
    inst.log.append(f"completed: {name}")
    inst.tokens.remove(name)
    inst.tokens.extend(t for t, _ in inst.process.outgoing(name))
    advance(inst)


if __name__ == "__main__":
    # Loan triage: run credit + KYC checks in parallel, then route on the score.
    loan = Process(
        nodes={
            "start":  Node("start", "start"),
            "fork":   Node("fork", "parallel"),
            "credit": Node("credit", "service",
                           handler=lambda v: v.update(score=v.get("score", 720))),
            "kyc":    Node("kyc", "service",
                           handler=lambda v: v.update(kyc_ok=True)),
            "join":   Node("join", "parallel"),
            "route":  Node("route", "exclusive"),
            "auto":   Node("auto", "service",
                           handler=lambda v: v.update(decision="auto-approved")),
            "review": Node("review", "user"),
            "done":   Node("done", "end"),
        },
        flows=[
            ("start", "fork", None),
            ("fork", "credit", None), ("fork", "kyc", None),
            ("credit", "join", None), ("kyc", "join", None),
            ("join", "route", None),
            ("route", "auto", lambda v: v["score"] >= 700),
            ("route", "review", None),                  # default flow
            ("auto", "done", None), ("review", "done", None),
        ],
    )

    good = start(loan, {"applicant": "meera"})
    assert good.complete and good.variables["decision"] == "auto-approved"
    print("score 720 ->", good.variables["decision"])

    risky = start(loan, {"applicant": "arjun", "score": 640})
    assert risky.tokens == ["review"]                   # parked at manual review
    print("score 640 -> waiting at", risky.tokens)
    complete_user_task(risky, "review", {"decision": "manually-approved"})
    assert risky.complete
    print("after review ->", risky.variables["decision"])
