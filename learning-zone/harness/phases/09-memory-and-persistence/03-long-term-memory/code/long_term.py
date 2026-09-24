"""Append-and-retrieve long-term memory (lexical ranking). Run: python3 long_term.py"""
import json
import os


class LongTermMemory:
    def __init__(self, path):
        self.path = path
        self.facts = json.load(open(path)) if os.path.exists(path) else []

    def remember(self, fact, tags=()):
        self.facts.append({"fact": fact, "tags": list(tags)})
        json.dump(self.facts, open(self.path, "w"))
        return "remembered"

    def retrieve(self, query, k=3):
        q = set(query.lower().split())

        def score(e):
            words = set(e["fact"].lower().split()) | set(e["tags"])
            return len(q & words)

        ranked = sorted(self.facts, key=score, reverse=True)
        return [e["fact"] for e in ranked[:k] if score(e) > 0]


if __name__ == "__main__":
    import tempfile
    m = LongTermMemory(tempfile.mktemp(suffix=".json"))
    m.remember("This project uses pnpm, not npm.", tags=["build"])
    m.remember("Auth flow lives in auth/.", tags=["auth"])
    print(m.retrieve("how do I build"))
    os.remove(m.path)
