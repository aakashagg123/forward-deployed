"""Token budgets and a cache-friendly request layout. Runs offline.

A real cache lives on the provider's side. This file models the one rule you control:
the prefix must be byte-identical between calls.   Run:  python3 code/cache_layout.py
"""
import json

MIN_CACHE_TOKENS = 512   # example value: the real minimum depends on the model


def estimate_tokens(text):
    """About 4 characters per token for English on older tokenizers; Opus 4.7 and later use about 30% more tokens, so this estimate runs low. Plan with it, never bill with it."""
    return max(1, round(len(text) / 4))


def request_tokens(req):
    """Estimate the input size of a whole request: tools + system + messages."""
    return estimate_tokens(json.dumps([req["tools"], req["system"], req["messages"]]))


def fits(req, max_output, limit):
    """Window rule: input + max_output must stay within the model limit."""
    used, room = request_tokens(req), limit - max_output
    return used <= room, used, room


def build_request(system_text, tools, history, user_text):
    """Order by volatility: tools, then system, then messages. Mark the end of the prefix."""
    system = [{"type": "text", "text": system_text,
               "cache_control": {"type": "ephemeral"}}]       # breakpoint
    messages = history + [{"role": "user", "content": user_text}]
    return {"tools": tools, "system": system, "messages": messages}


def cached_prefix(req):
    """Everything up to and including the block that carries cache_control."""
    return json.dumps([req["tools"], req["system"]], sort_keys=True)


def cache_hit(previous, new):
    """A hit needs an identical prefix that is long enough to be cached."""
    same = cached_prefix(previous) == cached_prefix(new)
    return same and estimate_tokens(cached_prefix(new)) >= MIN_CACHE_TOKENS


if __name__ == "__main__":
    TOOLS = [{"name": "read_file", "description": "Read a file.",
              "input_schema": {"type": "object", "properties": {}}}]
    STABLE = "You are a coding agent. Follow the project rules. " * 60

    first = build_request(STABLE, TOOLS, [], "List three git commands.")
    again = build_request(STABLE, TOOLS, [], "Now explain git rebase.")
    assert cache_hit(first, again)                       # only the last message changed

    stamped = build_request("Time: 10:41:07\n" + STABLE, TOOLS, [], "Now explain git rebase.")
    assert not cache_hit(first, stamped)                 # one early byte breaks the prefix

    other_tools = [dict(TOOLS[0], description="Read a file from disk.")]
    changed = build_request(STABLE, other_tools, [], "Now explain git rebase.")
    assert not cache_hit(first, changed)                 # tools come first, so this breaks it all

    short = build_request("Be brief.", TOOLS, [], "hi")
    assert not cache_hit(short, short)                   # too short to cache, even if identical

    ok, used, room = fits(first, max_output=1024, limit=4000)
    assert ok and room == 2976 and 700 < used < room
    assert not fits(first, max_output=1024, limit=1500)[0]
    print(f"ok: prefix ~{estimate_tokens(cached_prefix(first))} tokens, budget check works")
