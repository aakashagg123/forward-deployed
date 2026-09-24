"""History compaction: replace old turns with a synopsis. Run: python3 compaction.py"""


def compact(messages, est, max_tokens, summarize, keep_recent=4):
    def size(ms):
        return sum(est(str(m.get("content", ""))) for m in ms)

    if size(messages) <= max_tokens:
        return messages
    old, recent = messages[:-keep_recent], messages[-keep_recent:]
    synopsis = summarize(old)                        # model call in production
    note = {"role": "user", "content": f"[summary of earlier conversation]\n{synopsis}"}
    return [note] + recent


def stub_summarize(old):
    decisions = [m["content"] for m in old if m["role"] == "assistant"]
    return f"{len(old)} earlier messages. Key points: " + " | ".join(decisions[:3])


if __name__ == "__main__":
    est = lambda s: max(1, len(s) // 4)
    msgs = [{"role": "assistant", "content": f"decided thing {i}"} for i in range(20)]
    out = compact(msgs, est, max_tokens=50, summarize=stub_summarize)
    print("compacted to", len(out), "messages")
    print("synopsis:", out[0]["content"][:60], "…")
