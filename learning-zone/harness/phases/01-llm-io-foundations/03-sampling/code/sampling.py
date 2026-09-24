"""Temperature + top-p (nucleus) sampling over a toy distribution. Pure stdlib.

Run:  python3 sampling.py
"""
import math
import random


def softmax(logits, temp):
    t = max(temp, 1e-6)
    m = max(logits)
    exps = [math.exp((x - m) / t) for x in logits]
    s = sum(exps)
    return [e / s for e in exps]


def top_p_filter(probs, p):
    ranked = sorted(enumerate(probs), key=lambda kv: -kv[1])
    kept, cum = [], 0.0
    for i, pr in ranked:
        kept.append((i, pr))
        cum += pr
        if cum >= p:
            break
    z = sum(pr for _, pr in kept)
    return {i: pr / z for i, pr in kept}


def sample(logits, temp=1.0, p=1.0, rng=None):
    rng = rng or random.Random(0)
    probs = softmax(logits, temp)
    nucleus = top_p_filter(probs, p)
    r, acc = rng.random(), 0.0
    for i, pr in nucleus.items():
        acc += pr
        if r <= acc:
            return i
    return next(iter(nucleus))


if __name__ == "__main__":
    logits = [2.0, 1.0, 0.1, -1.0]
    print("greedy (temp~0):", sample(logits, temp=0.0001))
    print("varied (temp=1):", [sample(logits, temp=1.0, rng=random.Random(s)) for s in range(5)])
    print("top-p=0.5 nucleus:", top_p_filter(softmax(logits, 1.0), 0.5))
