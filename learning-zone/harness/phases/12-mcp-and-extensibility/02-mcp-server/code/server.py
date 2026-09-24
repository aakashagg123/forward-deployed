"""An MCP server (tools + resources) over a JSON-RPC dispatcher.

Self-contained (inlines the lesson-01 dispatcher) so it runs standalone.
Run:  python3 server.py
"""
import json


def request(id, method, params=None):
    return json.dumps({"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}})


def _response(id, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id}
    msg["error" if error else "result"] = error or result
    return json.dumps(msg)


class MCPServer:
    def __init__(self):
        self.tools = {}          # name -> (schema, fn)
        self.resources = {}      # uri -> content
        self.methods = {
            "tools/list": lambda p: [s for s, _ in self.tools.values()],
            "tools/call": self._call,
            "resources/read": lambda p: self.resources.get(p["uri"], ""),
        }

    def add_tool(self, name, schema, fn):
        self.tools[name] = ({**schema, "name": name}, fn)

    def add_resource(self, uri, content):
        self.resources[uri] = content

    def _call(self, params):
        name = params["name"]
        if name not in self.tools:
            raise ValueError(f"unknown tool {name}")
        return str(self.tools[name][1](**params.get("arguments", {})))

    def handle(self, raw):
        msg = json.loads(raw)
        fn = self.methods.get(msg["method"])
        if not fn:
            return _response(msg["id"], error={"code": -32601, "message": "method not found"})
        try:
            return _response(msg["id"], result=fn(msg.get("params", {})))
        except Exception as e:
            return _response(msg["id"], error={"code": -32603, "message": str(e)})


if __name__ == "__main__":
    srv = MCPServer()
    srv.add_tool("add", {"description": "Add.", "input_schema": {}}, lambda a, b: a + b)
    srv.add_resource("file://readme", "hello")
    print(srv.handle(request(1, "tools/list")))
    print(srv.handle(request(2, "tools/call", {"name": "add", "arguments": {"a": 2, "b": 3}})))
    print(srv.handle(request(3, "resources/read", {"uri": "file://readme"})))
