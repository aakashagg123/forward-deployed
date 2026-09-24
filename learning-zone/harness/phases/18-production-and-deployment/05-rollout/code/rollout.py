"""Canary routing + kill switch. Run:  python3 rollout.py"""
import hashlib


class Rollout:
    def __init__(self, stable, candidate, percent=10):
        self.stable, self.candidate, self.percent = stable, candidate, percent
        self.killed = False

    def kill(self):
        self.killed = True            # instant revert to stable

    def version_for(self, unit_id):
        if self.killed:
            return self.stable
        h = int(hashlib.sha256(unit_id.encode()).hexdigest(), 16) % 100
        return self.candidate if h < self.percent else self.stable


if __name__ == "__main__":
    r = Rollout("prompt-v3", "prompt-v4", percent=20)
    sample = [r.version_for(f"u{i}") for i in range(10)]
    print(sample.count("prompt-v4"), "of 10 on canary")
    r.kill()
    print("after kill:", set(r.version_for(f"u{i}") for i in range(10)))
