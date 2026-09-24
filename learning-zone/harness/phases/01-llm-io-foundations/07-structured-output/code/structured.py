"""Extract, repair, and validate JSON from a model's free-text reply. Stdlib only.

Run:  python3 structured.py
"""
import json
import re


def extract_json(text):
    """Grab the first balanced {...} block, ignoring surrounding prose/fences."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def repair(blob):
    blob = blob.strip().strip("`")                       # strip code fences
    blob = re.sub(r",\s*([}\]])", r"\1", blob)           # trailing commas
    return blob


def parse(text, required=()):
    blob = extract_json(text)
    if blob is None:
        return None, "no JSON object found"
    for candidate in (blob, repair(blob)):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        missing = [k for k in required if k not in obj]
        if missing:
            return None, f"missing keys {missing}"
        return obj, None
    return None, "unparseable JSON"


if __name__ == "__main__":
    msg = 'Sure! Here you go:\n```json\n{"name": "ada", "age": 36,}\n```'
    print(parse(msg, required=["name", "age"]))
    print(parse("no json here", required=["x"]))
