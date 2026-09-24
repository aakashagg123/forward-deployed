"""Pair-aware history truncation: drop oldest exchanges, never split tool pairs.

Run:  python3 truncate.py
"""


def truncate(messages, max_tokens, est, keep_recent=4):
    msgs = list(messages)

    def size(ms):
        return sum(est(str(m.get("content", ""))) for m in ms)

    while size(msgs) > max_tokens and len(msgs) > keep_recent:
        cut = 1
        while cut < len(msgs) - keep_recent and msgs[cut]["role"] == "tool":
            cut += 1                                  # advance past a tool_result
        del msgs[:cut]                                # drop a whole leading exchange
    return msgs


if __name__ == "__main__":
    est = lambda s: max(1, len(s) // 4)
    msgs = [{"role": "user", "content": "x" * 400} for _ in range(10)]
    out = truncate(msgs, max_tokens=200, est=est)
    print("kept", len(out), "of", len(msgs))
