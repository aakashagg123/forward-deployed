# needs: pip install anthropic and ANTHROPIC_API_KEY
"""The SDK does the SSE parsing and assembly for you. Run:  python3 code/streaming_sdk.py"""
import os

import anthropic

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")
client = anthropic.Anthropic()


def stream_turn(history, tools):
    """Print text live, then return the assembled message for the act step."""
    extra = {"tools": tools} if tools else {}
    with client.messages.stream(model=MODEL, max_tokens=1024,
                                messages=history, **extra) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        return stream.get_final_message()


if __name__ == "__main__":
    final = stream_turn([{"role": "user", "content": "Say hi in five words."}], tools=[])
    print("\nstop_reason:", final.stop_reason)
