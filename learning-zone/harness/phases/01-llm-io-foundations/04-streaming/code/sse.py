"""A from-scratch SSE parser + message assembler. Run:  python3 sse.py"""
import json


def parse_sse(lines):
    """Yield (event, data) pairs from raw SSE lines."""
    event, data = None, None
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data = json.loads(line[5:].strip())
        elif line == "":                              # blank line ends an event
            if event is not None:
                yield event, data
            event, data = None, None


def assemble(events):
    text = ""
    for event, data in events:
        if event == "content_block_delta":
            text += data["delta"]["text"]
    return text


if __name__ == "__main__":
    raw = [
        'event: content_block_delta', 'data: {"delta":{"text":"Hel"}}', '',
        'event: content_block_delta', 'data: {"delta":{"text":"lo"}}', '',
        'event: message_stop', 'data: {}', '',
    ]
    print(assemble(parse_sse(raw)))      # Hello
