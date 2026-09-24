"""The tool surface of a memory MCP server (transport added in Phase 12).

Run:  python3 memory_server.py
"""


class MemoryServer:
    """remember/recall over a durable store; .tools() are the MCP tool schemas."""

    def __init__(self, store):
        self.store = store                 # LongTermMemory from lesson 03

    def remember(self, fact, tags=None):
        return self.store.remember(fact, tags or [])

    def recall(self, query, k=3):
        return self.store.retrieve(query, k)

    def tools(self):
        return [
            {"name": "remember", "description": "Save a durable fact.",
             "input_schema": {"type": "object",
                              "properties": {"fact": {"type": "string"},
                                             "tags": {"type": "array"}},
                              "required": ["fact"]}},
            {"name": "recall", "description": "Retrieve relevant facts.",
             "input_schema": {"type": "object",
                              "properties": {"query": {"type": "string"},
                                             "k": {"type": "integer"}},
                              "required": ["query"]}},
        ]


if __name__ == "__main__":
    class Mem:                              # stand-in store
        def __init__(self):
            self.f = []

        def remember(self, fact, tags):
            self.f.append(fact)
            return "ok"

        def retrieve(self, q, k):
            return [x for x in self.f if any(w in x for w in q.split())][:k]

    s = MemoryServer(Mem())
    s.remember("Project uses pnpm.")
    print(s.recall("pnpm"))
    print([t["name"] for t in s.tools()])
