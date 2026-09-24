"""Measure TTFT vs. decode latency over a (streamed) call. Run:  python3 latency.py"""
import time


def measure(stream, now=time.perf_counter):
    start = now()
    ttft = None
    tokens = 0
    for _ in stream:
        if ttft is None:
            ttft = now() - start          # first token arrived
        tokens += 1
    total = now() - start
    decode = total - (ttft or 0)
    return {"ttft_s": round(ttft or 0, 4), "total_s": round(total, 4),
            "tokens": tokens,
            "per_token_ms": round(decode / max(tokens - 1, 1) * 1000, 2)}


if __name__ == "__main__":
    def fake_stream():
        time.sleep(0.05)            # prefill
        for _ in range(5):
            time.sleep(0.01)        # decode per token
            yield "tok"

    print(measure(fake_stream()))
