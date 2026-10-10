# needs: pip install anthropic and ANTHROPIC_API_KEY
"""Send two requests with the same prefix and watch the cache fill, then hit.

Run:  python3 code/cache_layout_sdk.py
The stable prefix must pass the model's minimum cacheable length or nothing is cached.
"""
import os

import anthropic

from cache_layout import build_request

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")
client = anthropic.Anthropic()
STABLE = "You are a coding agent. Follow the project rules. " * 200


def ask(user_text):
    req = build_request(STABLE, [], [], user_text)
    del req["tools"]                     # this demo has no tools; omit the empty list
    msg = client.messages.create(model=MODEL, max_tokens=256, **req)
    u = msg.usage
    print(f"input={u.input_tokens} cache_write={u.cache_creation_input_tokens} "
          f"cache_read={u.cache_read_input_tokens}")
    return msg


if __name__ == "__main__":
    ask("List three git commands.")      # first call writes the cache
    ask("Now explain git rebase.")       # second call reads it
    est = client.messages.count_tokens(
        model=MODEL, system=STABLE, messages=[{"role": "user", "content": "hi"}])
    print("counted input tokens:", est.input_tokens)
