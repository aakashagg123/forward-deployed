# needs: pip install anthropic and ANTHROPIC_API_KEY
"""Swap the scripted model for the real one. Everything else in agent.py stays the same. Not run offline.

Usage:  python3 code/agent_sdk.py /path/to/repo "Fix the failing test"
"""
import os
import sys

import anthropic

from agent import TOOL_SPECS, Agent

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")
SYSTEM = ("You are a coding agent working in one repo. Keep a todo list with the todo tool. "
          "Read before you edit. Run the tests before you say you are done.")

client = anthropic.Anthropic()


def sdk_model(history):
    """history in, content blocks out. agent.py already stores messages in the Messages API format."""
    reply = client.messages.create(
        model=MODEL, max_tokens=2048, system=SYSTEM, tools=TOOL_SPECS, messages=history)
    blocks = []
    for b in reply.content:
        if b.type == "text":
            blocks.append({"type": "text", "text": b.text})
        elif b.type == "tool_use":
            blocks.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
    return blocks


def ask_user(name, args):
    """The 'ask' verdict: a human decides. Anything but 'y' counts as no."""
    return input(f"allow {name} {args}? [y/N] ").strip().lower() == "y"


if __name__ == "__main__":
    root, task = sys.argv[1], sys.argv[2]
    result = Agent(root, sdk_model, approve=ask_user, max_steps=20).run(task)
    print(result["status"], result["steps"], result["text"])
