"""Layered config, a stable percentage flag, and a canary with a kill switch.

Run:  python3 code/rollout.py
"""
import hashlib


def load_config(defaults, *layers):
    """Later layers win. A value of None means 'not set here' and does not override."""
    cfg = dict(defaults)
    for layer in layers:
        cfg.update({k: v for k, v in layer.items() if v is not None})
    return cfg


def bucket(name, unit_id):
    """Map a unit (user, repo) to a stable number 0-99 for this flag."""
    return int(hashlib.sha256(f"{name}:{unit_id}".encode()).hexdigest(), 16) % 100


class Rollout:
    def __init__(self, name, stable, candidate, percent=10):
        self.name, self.stable, self.candidate, self.percent = name, stable, candidate, percent
        self.killed = False

    def kill(self):
        self.killed = True                  # one switch: everyone back to stable, no redeploy

    def version_for(self, unit_id):
        if self.killed:                     # checked first, so an incident never reasons about percent
            return self.stable
        return self.candidate if bucket(self.name, unit_id) < self.percent else self.stable


if __name__ == "__main__":
    # Config: file overrides defaults, env overrides file, and None never overrides.
    cfg = load_config({"model": "small", "max_steps": 10},
                      {"max_steps": 20}, {"model": "big", "max_steps": None})
    assert cfg == {"model": "big", "max_steps": 20}

    units = [f"user{i}" for i in range(1000)]
    r = Rollout("prompt-v4", "prompt-v3", "prompt-v4", percent=10)

    # A canary at 10% sends about 10% of 1000 units to the candidate.
    on_canary = {u for u in units if r.version_for(u) == "prompt-v4"}
    assert 70 <= len(on_canary) <= 130
    # The answer is stable: the same unit gets the same version on every call.
    assert all(r.version_for(u) == "prompt-v4" for u in list(on_canary)[:20])

    # Ramp up: raising the percent keeps every unit that was already on the canary.
    r.percent = 50
    wider = {u for u in units if r.version_for(u) == "prompt-v4"}
    assert on_canary <= wider and 420 <= len(wider) <= 580
    r.percent = 0
    assert not any(r.version_for(u) == "prompt-v4" for u in units)

    # Kill switch: even at 100%, everyone gets stable once it is thrown.
    r.percent = 100
    assert all(r.version_for(u) == "prompt-v4" for u in units)
    r.kill()
    assert {r.version_for(u) for u in units} == {"prompt-v3"}
    print(f"rollout ok: {len(on_canary)}/1000 on a 10% canary, {len(wider)}/1000 at 50%, kill switch holds")
