"""Token estimation + a context-budget guard (heuristic). Run: python3 tokens.py"""


def estimate_tokens(text):
    # ~4 chars/token for English; good enough for budgeting decisions.
    return max(1, round(len(text) / 4))


def messages_tokens(messages):
    return sum(estimate_tokens(m["content"]) for m in messages
               if isinstance(m.get("content"), str))


def fits(messages, max_output, limit):
    used = messages_tokens(messages)
    headroom = limit - max_output
    return used <= headroom, used, headroom


def trim_to_budget(messages, max_output, limit, keep_last=2):
    """Drop oldest messages (after the first) until input fits, keeping recent turns."""
    msgs = list(messages)
    ok, *_ = fits(msgs, max_output, limit)
    while not ok and len(msgs) > keep_last + 1:
        del msgs[1]                                  # keep msgs[0]; drop next-oldest
        ok, *_ = fits(msgs, max_output, limit)
    return msgs


if __name__ == "__main__":
    msgs = [{"role": "user", "content": "x" * 4000}]      # ~1000 tokens
    print("fits?", fits(msgs, max_output=500, limit=1200))
    big = [{"role": "user", "content": "sys"}] + [
        {"role": "user", "content": "y" * 4000} for _ in range(3)]
    print("trimmed len:", len(trim_to_budget(big, 200, 1200)))
