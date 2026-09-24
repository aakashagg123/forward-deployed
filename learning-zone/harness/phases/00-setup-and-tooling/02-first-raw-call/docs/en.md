# Your first raw model call (HTTP, no SDK)

> **Motto** — The SDK is a convenience; underneath, a model call is one HTTPS POST.

*Part of Phase 00 — Setup & Tooling.*

## The Problem

If the model is a black box, every later debugging session is guesswork. Before you lean
on the SDK, make one call with nothing but `urllib`. Watch exactly what goes over the
wire: the URL, the headers (including the API key and version), and the JSON body.
Then the SDK holds no mysteries.

## The Concept

A message request is a POST to `/v1/messages` with three header essentials and a small
JSON body:

```
POST https://api.anthropic.com/v1/messages
  x-api-key: <key>
  anthropic-version: 2023-06-01
  content-type: application/json
  { "model": "...", "max_tokens": N, "messages": [ {role, content} ] }
```

The response JSON has a `content` array of blocks. For plain text, read
`content[0].text`.

## Build It

`code/raw_call.py` — stdlib only, no `anthropic` package:

```python
import json, os, urllib.request

def call(prompt, model="claude-opus-5", max_tokens=256):
    body = json.dumps({
        "model": model, "max_tokens": max_tokens,
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
```

Run it (with `ANTHROPIC_API_KEY` set). You just talked to the model with zero
dependencies — proof that the harness is yours to control end to end.

## Use It

The same call via the SDK is `anthropic.Anthropic().messages.create(...)`. It adds
retries, typing, streaming, and error classes — all conveniences over this exact POST.
You'll use the SDK from here on, but you know what it's doing.

## Ship It

[`outputs/prompt-three-words.md`](../../02-first-raw-call/outputs/prompt-three-words.md) — a
tiny reusable smoke-test prompt to confirm connectivity from any tool.

## Check Yourself

**Q1.** Which header carries the API key?

- A) `authorization`
- B) `x-api-key`
- C) `content-type`
- D) `anthropic-version`

<details><summary>Answer</summary>B — `x-api-key` (with `anthropic-version` required
too).</details>

**Q2.** Where is the text in the response?

- A) the top-level `text` field
- B) inside the `content` array of blocks
- C) the `messages` field
- D) the headers

<details><summary>Answer</summary>B — `content` is a list of typed blocks; read the
`text` ones.</details>

**Challenge.** Add error handling: catch `urllib.error.HTTPError`, print the status code
and the JSON error body, so a 401 (bad key) or 429 (rate limit) is legible.

## Related

- Builds on: [Dev environment & the SDK](../../01-dev-environment/docs/en.md)
- Next: [API keys, secrets & env hygiene](../../03-secrets-and-env/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
