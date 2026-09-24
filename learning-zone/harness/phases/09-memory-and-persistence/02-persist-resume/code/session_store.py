"""Save/load a full session (history + scratchpad). Run:  python3 session_store.py"""
import json
import os


class SessionStore:
    def __init__(self, path):
        self.path = path

    def save(self, history, scratch):
        with open(self.path, "w") as f:
            json.dump({"history": history, "scratch": scratch}, f, indent=2)
        return f"saved {len(history)} messages"

    def load(self):
        if not os.path.exists(self.path):
            return [], {}
        with open(self.path) as f:
            data = json.load(f)
        return data.get("history", []), data.get("scratch", {})


if __name__ == "__main__":
    import tempfile
    store = SessionStore(tempfile.mktemp(suffix=".json"))
    print(store.save([{"role": "user", "content": "hi"}], {"editing": "a.py"}))
    hist, scratch = store.load()
    print(len(hist), scratch)
    os.remove(store.path)
