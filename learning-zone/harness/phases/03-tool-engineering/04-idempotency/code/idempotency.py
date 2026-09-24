"""Idempotency for side-effecting tools: dedupe calls by an intent-derived key.

Run:  python3 idempotency.py
"""
import hashlib
import json


class Idempotent:
    def __init__(self):
        self._done = {}                        # key -> result

    def run(self, key, action):
        if key in self._done:
            return self._done[key], "replayed"
        result = action()                      # the real side effect
        self._done[key] = result
        return result, "executed"


def key_for(tool, args):
    blob = json.dumps([tool, args], sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


if __name__ == "__main__":
    idem = Idempotent()
    sends = []

    def send():
        sends.append("email")
        return "sent"

    k = key_for("send_email", {"to": "a@b.com"})
    print(idem.run(k, send))     # ('sent', 'executed')
    print(idem.run(k, send))     # ('sent', 'replayed')
    print("emails actually sent:", len(sends))   # 1
