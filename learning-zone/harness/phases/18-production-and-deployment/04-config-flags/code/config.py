"""Layered config + percentage feature flags. Run:  python3 config.py"""
import hashlib


def load_config(defaults, *overrides):
    cfg = dict(defaults)
    for o in overrides:
        cfg.update({k: v for k, v in o.items() if v is not None})
    return cfg


def flag_enabled(name, unit_id, percent):
    """Stable per-unit rollout: same unit_id always gets the same answer."""
    h = int(hashlib.sha256(f"{name}:{unit_id}".encode()).hexdigest(), 16) % 100
    return h < percent


if __name__ == "__main__":
    cfg = load_config({"model": "haiku", "max_steps": 10},
                      {"model": "claude-opus-5"})
    print(cfg["model"], cfg["max_steps"])
    print([flag_enabled("new_planner", u, 30) for u in ["u1", "u2", "u3", "u4"]])
