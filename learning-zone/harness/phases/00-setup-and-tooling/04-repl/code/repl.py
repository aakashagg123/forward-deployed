"""A minimal conversational REPL over the model — the smallest useful harness.

Requires ANTHROPIC_API_KEY and the `anthropic` package. Run:  python3 repl.py
Type 'exit' to quit. Defaults to Claude Opus 5 (claude-opus-5).
"""
import anthropic

client = anthropic.Anthropic()


def repl(model="claude-opus-5"):
    history = []
    print("Talk to the model (type 'exit' to quit).")
    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user in ("exit", "quit"):
            break
        history.append({"role": "user", "content": user})
        msg = client.messages.create(model=model, max_tokens=1024, messages=history)
        text = "".join(b.text for b in msg.content if b.type == "text")
        print("ai>", text)
        history.append({"role": "assistant", "content": text})


if __name__ == "__main__":
    repl()
