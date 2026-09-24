"""Cache-aware request builder composing the context phase.

Requires the `anthropic` package + ANTHROPIC_API_KEY to run live.
Defaults to Claude Opus 5 (claude-opus-5).
"""
import anthropic

client = anthropic.Anthropic()


def build_request(memory, tools, history, files, user_msg):
    system = [{
        "type": "text",
        "text": "You are a coding agent.\n\n" + memory,     # stable: persona + project memory
        "cache_control": {"type": "ephemeral"},             # breakpoint after stable prefix
    }]
    messages = list(history)                                 # compacted (lesson 04)
    if files:
        messages.append({"role": "user", "content": files})  # this-turn, wrapped (lesson 05)
    messages.append({"role": "user", "content": user_msg})
    return dict(model="claude-opus-5", max_tokens=1024,
                system=system, tools=tools, messages=messages)


if __name__ == "__main__":
    req = build_request(memory="Project: use the public API barrel.",
                        tools=[], history=[], files=None, user_msg="Add subtract().")
    print("system blocks:", len(req["system"]),
          "cache:", req["system"][0]["cache_control"]["type"])
    # client.messages.create(**req)  # uncomment with a key set
