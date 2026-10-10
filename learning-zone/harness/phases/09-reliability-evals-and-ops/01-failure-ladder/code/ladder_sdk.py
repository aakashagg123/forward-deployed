# needs: pip install anthropic and ANTHROPIC_API_KEY
"""The same ladder over the Anthropic SDK. Not run offline.

The SDK retries some errors by default (max_retries=2). We set max_retries=0 so the
ladder owns every retry, and the attempts do not multiply.
"""
import json
import os
import time

import anthropic

from ladder import Transient, climb

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")
FALLBACK = os.environ.get("HARNESS_FALLBACK_MODEL")      # optional second rung

client = anthropic.Anthropic(max_retries=0)
TASK = 'Return JSON with the keys "name" and "age" for Ada Lovelace. Return only JSON.'


def call_model(model, feedback):
    prompt = TASK if feedback is None else f"{TASK}\n\n{feedback}"
    try:
        reply = client.messages.create(
            model=model, max_tokens=256, messages=[{"role": "user", "content": prompt}])
    except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
        raise Transient(str(e)) from e                   # 429, network, and 5xx errors may pass
    return reply.content[0].text                         # 400-class errors are not caught: fail fast


def validate(text):
    try:
        return None if {"name", "age"} <= set(json.loads(text)) else "need keys name and age"
    except ValueError as e:
        return f"not valid JSON: {e}"


if __name__ == "__main__":
    chain = [MODEL] + ([FALLBACK] if FALLBACK else [])
    print(climb(chain, call_model, validate, sleep=time.sleep))
