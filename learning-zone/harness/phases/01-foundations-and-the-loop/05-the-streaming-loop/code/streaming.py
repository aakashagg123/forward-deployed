"""Streaming: parse server-sent events into a message, print text live, then act.

Events follow the Messages API stream format. Runs offline:  python3 code/streaming.py
"""
import json
import sys


class StreamError(Exception):
    pass


def parse_sse(lines):
    """Yield (event, data) pairs from raw SSE lines. A blank line ends an event."""
    event, data = None, []
    for line in list(lines) + [""]:                    # the final "" flushes the last event
        line = line.rstrip("\n")
        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data.append(line[5:].strip())
        elif line == "" and (event or data):
            yield event, json.loads("\n".join(data)) if data else {}
            event, data = None, []


def assemble(events, on_text=lambda t: None):
    """Fold events into (content blocks, stop_reason). Tool JSON is parsed only at block stop."""
    blocks, partial, stop = {}, {}, None
    for name, ev in events:
        kind, i = ev.get("type", name), ev.get("index")
        if kind == "error":
            raise StreamError(ev["error"]["message"])
        if kind == "content_block_start":
            blocks[i], partial[i] = dict(ev["content_block"]), ""
        elif kind == "content_block_delta":
            d = ev["delta"]
            if d["type"] == "text_delta":
                blocks[i]["text"] += d["text"]
                on_text(d["text"])                     # live output
            elif d["type"] == "input_json_delta":
                partial[i] += d["partial_json"]        # a fragment, not valid JSON yet
        elif kind == "content_block_stop" and blocks[i]["type"] == "tool_use":
            try:
                blocks[i]["input"] = json.loads(partial[i] or "{}")
            except json.JSONDecodeError as exc:
                raise StreamError(f"incomplete tool input: {exc}") from exc
        elif kind == "message_delta":
            stop = ev["delta"]["stop_reason"]
        # message_start, ping, message_stop and unknown events are ignored on purpose
    if stop is None:
        raise StreamError("stream ended before message_delta")
    return [blocks[i] for i in sorted(blocks)], stop


def run(query, stream_model, tools, on_text=sys.stdout.write, max_steps=5):
    """The same loop as before. Only how the message arrives has changed."""
    history = [{"role": "user", "content": query}]
    for _ in range(max_steps):
        blocks, stop = assemble(parse_sse(stream_model(history)), on_text)
        history.append({"role": "assistant", "content": blocks})
        calls = [b for b in blocks if b["type"] == "tool_use"]
        if stop != "tool_use" or not calls:
            return "".join(b["text"] for b in blocks if b["type"] == "text")
        results = [{"type": "tool_result", "tool_use_id": c["id"],
                    "content": str(tools[c["name"]](**c["input"]))} for c in calls]
        history.append({"role": "user", "content": results})
    return "stopped: max_steps"


def sse(*events):
    """Render events as raw SSE lines, the way they arrive on the wire."""
    lines = []
    for ev in events:
        lines += [f"event: {ev['type']}", "data: " + json.dumps(ev), ""]
    return lines


def text_block(i, *chunks):
    return ([{"type": "content_block_start", "index": i, "content_block": {"type": "text", "text": ""}}]
            + [{"type": "content_block_delta", "index": i, "delta": {"type": "text_delta", "text": c}}
               for c in chunks] + [{"type": "content_block_stop", "index": i}])


def tool_block(i, call_id, name, *fragments):
    return ([{"type": "content_block_start", "index": i,
              "content_block": {"type": "tool_use", "id": call_id, "name": name, "input": {}}}]
            + [{"type": "content_block_delta", "index": i,
                "delta": {"type": "input_json_delta", "partial_json": f}} for f in fragments]
            + [{"type": "content_block_stop", "index": i}])


def message(stop, *blocks):
    return sse({"type": "message_start"}, {"type": "ping"}, *[e for b in blocks for e in b],
               {"type": "message_delta", "delta": {"stop_reason": stop}}, {"type": "message_stop"})


def fake_stream(history):
    if isinstance(history[-1]["content"], str):        # first turn: text, then a tool call
        return message("tool_use", text_block(0, "Let ", "me ", "add ", "those.\n"),
                       tool_block(1, "t1", "add", "", '{"a": 2', ', "b": 3}'))
    return message("end_turn", text_block(0, "The answer is ",
                                          history[-1]["content"][0]["content"], ".\n"))


if __name__ == "__main__":
    live = []
    answer = run("2 + 3?", fake_stream, {"add": lambda a, b: a + b}, on_text=live.append)
    assert answer == "The answer is 5.\n", answer
    assert live[:4] == ["Let ", "me ", "add ", "those.\n"]       # text arrived in pieces
    blocks, stop = assemble(parse_sse(fake_stream([{"role": "user", "content": "q"}])))
    assert stop == "tool_use" and blocks[1]["input"] == {"a": 2, "b": 3}

    bad_json = message("tool_use", tool_block(0, "t1", "add", '{"a": 2'))   # JSON never closes
    no_end = [l for l in message("end_turn", text_block(0, "hi")) if "message_delta" not in l]
    overload = sse({"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}})
    for bad, why in [(bad_json, "incomplete tool input"), (no_end, "stream ended"),
                     (overload, "Overloaded")]:
        try:
            assemble(parse_sse(bad))
            raise SystemExit("a bad stream was accepted")
        except StreamError as exc:
            assert why in str(exc), exc
    print("ok:", repr(answer))
