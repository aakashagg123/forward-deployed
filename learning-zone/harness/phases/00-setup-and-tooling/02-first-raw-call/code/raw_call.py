"""One model call with the standard library only — no `anthropic` package.

Requires ANTHROPIC_API_KEY. Run:  python3 raw_call.py
Defaults to the latest model, Claude Opus 5 (claude-opus-5).
"""
import json
import os
import urllib.request


def call(prompt, model="claude-opus-5", max_tokens=256):
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body, method="POST",
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        })
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    return "".join(b["text"] for b in data["content"] if b["type"] == "text")


if __name__ == "__main__":
    print(call("Say hello in exactly three words."))
