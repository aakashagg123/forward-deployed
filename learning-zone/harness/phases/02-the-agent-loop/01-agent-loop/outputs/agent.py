"""Ship It — a reusable, model-agnostic agent loop.

kind: module  ·  phase: 02  ·  lesson: 01

Plug in any `model` callable (messages -> {"text", "tool_calls"}) and a `tools`
dict (name -> callable). Later phases extend this with real dispatch (P3),
context management (P4), budgets and retries (P14), and observability (P16)
without touching the core three invariants.

    from agent import Agent
    Agent(model=my_model, tools={"add": lambda a, b: str(a + b)}).run("2 + 3?")
"""
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Agent:
    model: Callable               # messages -> {"text": str, "tool_calls": [...]}
    tools: dict                   # name -> callable
    max_steps: int = 10
    on_step: Callable | None = None   # hook for tracing/observability (Phase 16)
    history: list = field(default_factory=list)

    def run(self, query: str) -> str:
        self.history.append({"role": "user", "content": query})
        for step in range(self.max_steps):
            msg = self.model(self.history)
            self.history.append({"role": "assistant", "content": msg["text"]})
            if self.on_step:
                self.on_step(step, msg)
            calls = msg.get("tool_calls") or []
            if not calls:                                   # termination
                return msg["text"]
            for call in calls:
                self.history.append({
                    "role": "tool",
                    "name": call["name"],
                    "content": self._dispatch(call),
                })
        return "stopped: hit max_steps"

    def _dispatch(self, call: dict) -> str:
        fn = self.tools.get(call["name"])
        if fn is None:
            return f"error: no tool named {call['name']}"
        try:
            return str(fn(**call.get("args", {})))
        except Exception as e:                              # errors are data, not crashes
            return f"error: {e}"
