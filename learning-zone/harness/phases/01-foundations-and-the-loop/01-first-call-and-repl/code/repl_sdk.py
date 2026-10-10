# needs: pip install anthropic and ANTHROPIC_API_KEY
"""The same REPL on the official SDK. Run:  python3 code/repl_sdk.py"""
import anthropic

from repl import MODEL, SYSTEM, repl      # MODEL is defined once, in repl.py

client = anthropic.Anthropic()


def send(history):
    msg = client.messages.create(model=MODEL, max_tokens=1024,
                                 system=SYSTEM, messages=history)
    return "".join(b.text for b in msg.content if b.type == "text")


if __name__ == "__main__":
    print("Talk to the model (type 'exit' to quit).")
    repl(send)
