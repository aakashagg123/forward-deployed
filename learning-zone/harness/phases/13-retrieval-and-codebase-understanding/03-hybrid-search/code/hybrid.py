"""Reciprocal-rank-fusion hybrid search over ranked lists. Run: python3 hybrid.py"""


def rrf(*ranked_lists, k=60):
    scores = {}
    for lst in ranked_lists:
        for rank, doc in enumerate(lst):
            scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)
    return [d for d, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)]


if __name__ == "__main__":
    lexical = ["auth.py", "utils.py", "session.py"]
    semantic = ["session.py", "auth.py", "login_flow.py"]
    print(rrf(lexical, semantic))
