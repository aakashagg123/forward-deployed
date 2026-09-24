"""A streaming agent loop: print text live, accumulate the message, then act.

A fake streamed model (a generator of deltas) proves the accumulation logic with
no network. Loop termination and act steps are unchanged from earlier lessons.

Run:  python3 streaming.py
"""
import sys


def fake_stream(history):
    """Yield deltas like a real streaming API: text chunks, then maybe a tool call."""
    if not any(m["role"] == "tool" for m in history):
        for chunk in ["Let ", "me ", "add ", "those.\n"]:
            yield {"type": "text", "text": chunk}
        yield {"type": "tool_use", "name": "add", "args": {"a": 2, "b": 3}}
    else:
        for chunk in ["The ", "answer ", "is ", history[-1]["content"], ".\n"]:
            yield {"type": "text", "text": chunk}


def stream_turn(history, model, on_text):
    """Consume the stream, emit text live, return the assembled message."""
    text, tool_calls = "", []
    for delta in model(history):
        if delta["type"] == "text":
            on_text(delta["text"])               # live output
            text += delta["text"]
        elif delta["type"] == "tool_use":
            tool_calls.append({"name": delta["name"], "args": delta["args"]})
    return {"text": text, "tool_calls": tool_calls}


def run(query, model, tools, max_steps=10):
    history = [{"role": "user", "content": query}]
    for _ in range(max_steps):
        msg = stream_turn(history, model, on_text=sys.stdout.write)
        history.append({"role": "assistant", "content": msg["text"]})
        if not msg["tool_calls"]:                 # same termination as lesson 03
            return msg["text"]
        for call in msg["tool_calls"]:            # same act step as lesson 02
            out = str(tools[call["name"]](**call["args"]))
            history.append({"role": "tool", "content": out})
    return "stopped: max_steps"


if __name__ == "__main__":
    run("2 + 3?", fake_stream, {"add": lambda a, b: a + b})
