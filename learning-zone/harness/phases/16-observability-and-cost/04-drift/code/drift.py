"""A rolling-window drift detector. Run:  python3 drift.py"""


def detect_drift(history, window=5, threshold=0.05):
    """history: metric values over time (oldest -> newest)."""
    if len(history) < window * 2:
        return {"drift": False, "reason": "not enough data"}
    baseline = history[-window * 2:-window]
    recent = history[-window:]
    b, r = sum(baseline) / window, sum(recent) / window
    return {"drift": (b - r) > threshold, "baseline": round(b, 3),
            "recent": round(r, 3), "delta": round(r - b, 3)}


if __name__ == "__main__":
    healthy = [0.9, 0.91, 0.9, 0.92, 0.9, 0.91, 0.9, 0.9, 0.91, 0.9]
    drifting = [0.9, 0.9, 0.91, 0.9, 0.9, 0.82, 0.8, 0.81, 0.79, 0.8]
    print("healthy:", detect_drift(healthy))
    print("drifting:", detect_drift(drifting))
