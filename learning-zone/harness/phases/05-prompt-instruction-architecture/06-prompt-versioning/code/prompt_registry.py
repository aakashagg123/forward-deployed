"""Versioned prompt registry with rollback + a tiny A/B harness.

Run:  python3 prompt_registry.py
"""
from dataclasses import dataclass, field


@dataclass
class PromptRegistry:
    versions: dict = field(default_factory=dict)     # name -> {version: text}
    active: dict = field(default_factory=dict)       # name -> version

    def register(self, name, version, text, activate=False):
        self.versions.setdefault(name, {})[version] = text
        if activate or name not in self.active:
            self.active[name] = version

    def get(self, name, version=None):
        return self.versions[name][version or self.active[name]]

    def rollback(self, name, version):
        self.active[name] = version


def ab_test(registry, name, va, vb, eval_set, run, score):
    """run(prompt, case)->output; score(output, case)->0..1. Returns mean scores."""
    def mean(v):
        outs = [score(run(registry.get(name, v), c), c) for c in eval_set]
        return sum(outs) / len(outs)
    return {va: mean(va), vb: mean(vb)}


if __name__ == "__main__":
    r = PromptRegistry()
    r.register("sys", "v1", "Be terse.", activate=True)
    r.register("sys", "v2", "Be terse. Always cite files.")
    res = ab_test(r, "sys", "v1", "v2",
                  eval_set=[{"want": "cite"}],
                  run=lambda p, c: p,
                  score=lambda o, c: 1.0 if c["want"] in o.lower() else 0.0)
    print(res)                       # {'v1': 0.0, 'v2': 1.0}
    r.rollback("sys", "v1")
    print("active:", r.active["sys"])
