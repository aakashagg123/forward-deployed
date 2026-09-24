"""Cache-aware request layout: stable prefix marked cacheable, volatile turn last.

Requires the `anthropic` package + ANTHROPIC_API_KEY to run live.
Defaults to Claude Opus 5 (claude-opus-5).
"""
import anthropic

client = anthropic.Anthropic()

SYSTEM = [
    {
        "type": "text",
        "text": "You are a coding agent. <long stable instructions...>",
        "cache_control": {"type": "ephemeral"},          # cache breakpoint
    },
]


def ask(user_text, tools):
    return client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        system=SYSTEM,                                    # stable, cached
        tools=tools,                                      # stable, place before volatile
        messages=[{"role": "user", "content": user_text}],  # volatile, last
    )


if __name__ == "__main__":
    # Illustrative: requires network + key. Two identical-prefix calls populate then hit cache.
    r = ask("List three git commands.", tools=[])
    u = r.usage
    print("cache_creation:", getattr(u, "cache_creation_input_tokens", None),
          "cache_read:", getattr(u, "cache_read_input_tokens", None))
