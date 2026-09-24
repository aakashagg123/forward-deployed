"""An MCP client: discover and invoke a server's tools. Run:  python3 client.py

Self-contained: includes a tiny in-process server to talk to.
"""
import json


class _TinyServer:
    def __init__(self):
        self.tools = {"add": ({"name": "add", "description": "Add."},
                              lambda a, b: a + b)}

    def handle(self, raw):
        m = json.loads(raw)
        if m["method"] == "tools/list":
            result = [s for s, _ in self.tools.values()]
        elif m["method"] == "tools/call":
            p = m["params"]
            result = str(self.tools[p["name"]][1](**p.get("arguments", {})))
        else:
            return json.dumps({"jsonrpc": "2.0", "id": m["id"],
                               "error": {"code": -32601, "message": "method not found"}})
        return json.dumps({"jsonrpc": "2.0", "id": m["id"], "result": result})


class MCPClient:
    def __init__(self, server):
        self.server = server
        self._id = 0

    def _rpc(self, method, params=None):
        self._id += 1
        raw = json.dumps({"jsonrpc": "2.0", "id": self._id,
                          "method": method, "params": params or {}})
        return json.loads(self.server.handle(raw))

    def list_tools(self):
        return self._rpc("tools/list").get("result", [])

    def call(self, name, **arguments):
        r = self._rpc("tools/call", {"name": name, "arguments": arguments})
        return r.get("result", r.get("error"))


if __name__ == "__main__":
    client = MCPClient(_TinyServer())
    print("discovered:", [t["name"] for t in client.list_tools()])
    print("add(2,3) ->", client.call("add", a=2, b=3))
