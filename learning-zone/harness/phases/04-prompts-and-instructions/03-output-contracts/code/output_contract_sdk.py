# needs: pip install anthropic and ANTHROPIC_API_KEY
"""Ask the API for schema-shaped JSON, then verify it anyway. Not run offline.

Run:  python3 code/output_contract_sdk.py
"""
import os

import anthropic

from contract import check_json, extract_blob

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")

SCHEMA = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    "required": ["name", "age"],
    "additionalProperties": False,
}

client = anthropic.Anthropic()
response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": "Extract the person: Ada Lovelace, aged 36."}],
    output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
)
text = next(b.text for b in response.content if b.type == "text")
problems = check_json(text, {"name": str, "age": int})     # trust, but verify
print(extract_blob(text), problems or "conforms")
