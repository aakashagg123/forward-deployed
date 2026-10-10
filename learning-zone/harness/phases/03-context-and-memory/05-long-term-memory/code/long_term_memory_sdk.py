# needs: pip install anthropic and ANTHROPIC_API_KEY
"""Claude's built-in memory tool, backed by a local folder. Not run offline.

Claude asks for file operations under /memories. This SDK helper runs them against ./memory.
Run:  python3 code/long_term_memory_sdk.py
"""
import os

import anthropic
from anthropic.tools import BetaLocalFilesystemMemoryTool

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")

client = anthropic.Anthropic()
memory = BetaLocalFilesystemMemoryTool(base_path="./memory")

runner = client.beta.messages.tool_runner(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user",
               "content": "Remember that this project uses pnpm, not npm."}],
    tools=[memory],
)
final_message = runner.until_done()
print(final_message.content)
