"""A CI regression gate: fail the build if the eval score dropped. Run: python3 gate.py"""


def gate(current, baseline, tolerance=0.02):
    """Return (passed, message). Fails if current dropped > tolerance below baseline."""
    delta = current - baseline
    if delta < -tolerance:
        return False, f"REGRESSION: {current:.3f} < baseline {baseline:.3f} (Δ{delta:+.3f})"
    return True, f"ok: {current:.3f} vs baseline {baseline:.3f} (Δ{delta:+.3f})"


def main(current, baseline):
    passed, msg = gate(current, baseline)
    print(msg)
    return 0 if passed else 1        # nonzero exit fails CI


if __name__ == "__main__":
    print(gate(0.91, 0.90))
    print(gate(0.85, 0.90))
