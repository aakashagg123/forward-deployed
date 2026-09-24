"""History: conversation state with tool-call pairing invariants and serialization.

Run:  python3 history.py
"""
import json
from dataclasses import dataclass, field


@dataclass
class History:
    messages: list = field(default_factory=list)
    _pending: set = field(default_factory=set)          # tool_use ids awaiting results

    def user(self, text):
        self.messages.append({"role": "user", "content": text})

    def assistant(self, text, tool_calls=None):
        msg = {"role": "assistant", "content": text, "tool_calls": tool_calls or []}
        self.messages.append(msg)
        self._pending = {c["id"] for c in msg["tool_calls"]}

    def tool_result(self, call_id, content):
        if call_id not in self._pending:
            raise ValueError(f"result for unknown/unpaired call {call_id!r}")
        self.messages.append({"role": "tool", "call_id": call_id, "content": content})
        self._pending.discard(call_id)

    def complete(self):
        """True when every requested tool call has a result — safe to call the model."""
        return not self._pending

    def dump(self):
        return json.dumps(self.messages, indent=2)

    @classmethod
    def load(cls, blob):
        return cls(messages=json.loads(blob))


if __name__ == "__main__":
    h = History()
    h.user("what is 2 + 3?")
    h.assistant("let me add", tool_calls=[{"id": "t1", "name": "add", "args": {"a": 2, "b": 3}}])
    print("complete before result:", h.complete())      # False
    h.tool_result("t1", "5")
    print("complete after result: ", h.complete())      # True
    print("round-trips:", History.load(h.dump()).messages == h.messages)
