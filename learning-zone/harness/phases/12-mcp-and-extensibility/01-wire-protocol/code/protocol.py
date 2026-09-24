"""JSON-RPC 2.0 framing + a method dispatcher (the core of MCP). Run: python3 protocol.py"""
import json


def request(id, method, params=None):
    return json.dumps({"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}})


def response(id, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id}
    msg["error" if error else "result"] = error or result
    return json.dumps(msg)


class Dispatcher:
    def __init__(self):
        self.methods = {}

    def method(self, name):
        def deco(fn):
            self.methods[name] = fn
            return fn
        return deco

    def handle(self, raw):
        msg = json.loads(raw)
        fn = self.methods.get(msg["method"])
        if not fn:
            return response(msg["id"], error={"code": -32601, "message": "method not found"})
        try:
            return response(msg["id"], result=fn(msg.get("params", {})))
        except Exception as e:
            return response(msg["id"], error={"code": -32603, "message": str(e)})


if __name__ == "__main__":
    d = Dispatcher()
    d.method("ping")(lambda p: "pong")
    print(d.handle(request(1, "ping")))
    print(d.handle(request(2, "nope")))
