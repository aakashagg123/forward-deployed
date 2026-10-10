"""A tiny MCP server and client over stdio, from scratch (spec 2025-06-18 shapes).

Run:  python3 code/mcp_stdio.py          (client spawns the server as a subprocess)
      python3 code/mcp_stdio.py --serve  (server only, reads stdin, writes stdout)
"""
import json
import subprocess
import sys

TOOLS = [
    {"name": "add", "description": "Add two integers.",
     "inputSchema": {"type": "object", "properties": {"a": {"type": "integer"},
                     "b": {"type": "integer"}}, "required": ["a", "b"]}},
    {"name": "divide", "description": "Divide a by b.",
     "inputSchema": {"type": "object", "properties": {"a": {"type": "number"},
                     "b": {"type": "number"}}, "required": ["a", "b"]}},
]


def run_tool(name, args):
    if name == "add":
        return args["a"] + args["b"]
    if name == "divide":
        return args["a"] / args["b"]          # b == 0 raises: a tool failure
    raise KeyError(name)


def handle(msg, state):
    """Return a response dict, or None for a notification (no id, no reply)."""
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:                           # notification
        if method == "notifications/initialized":
            state["ready"] = True
        return None
    if method == "initialize":
        result = {"protocolVersion": "2025-06-18",
                  "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": "demo", "title": "Demo server", "version": "0.1.0"}}
    elif method in ("tools/list", "tools/call") and not state.get("ready"):
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32600, "message": "not initialized"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        p = msg.get("params", {})
        if p.get("name") not in {t["name"] for t in TOOLS}:      # protocol error
            return {"jsonrpc": "2.0", "id": mid, "error": {
                "code": -32602, "message": f"Unknown tool: {p.get('name')}"}}
        try:
            text, is_error = str(run_tool(p["name"], p.get("arguments", {}))), False
        except Exception as e:                # tool failure: a result with isError
            text, is_error = f"{type(e).__name__}: {e}", True
        result = {"content": [{"type": "text", "text": text}], "isError": is_error}
    else:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve():
    state = {}
    for line in sys.stdin:                    # one JSON message per line
        try:
            reply = handle(json.loads(line), state)
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None,
                     "error": {"code": -32700, "message": "parse error"}}
        print("server saw:", line.strip()[:40], file=sys.stderr)   # logs go to stderr
        if reply is not None:
            print(json.dumps(reply), flush=True)                    # stdout: protocol only


class StdioClient:
    def __init__(self):
        self.p = subprocess.Popen([sys.executable, __file__, "--serve"], text=True,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self.n = 0

    def notify(self, method):
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n")
        self.p.stdin.flush()

    def request(self, method, params=None):
        self.n += 1
        msg = {"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}}
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        reply = json.loads(self.p.stdout.readline())     # must be valid JSON, or we fail
        assert reply["id"] == self.n
        return reply

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=5)
        return self.p.stderr.read()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        serve()
        sys.exit(0)
    c = StdioClient()
    early = c.request("tools/list")                      # before the handshake
    assert early["error"]["code"] == -32600
    init = c.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                     "clientInfo": {"name": "demo-client", "title": "Demo", "version": "0.1"}})
    assert init["result"]["protocolVersion"] == "2025-06-18"
    assert init["result"]["serverInfo"]["name"] == "demo"
    c.notify("notifications/initialized")                # a notification: no reply
    tools = c.request("tools/list")["result"]["tools"]
    assert [t["name"] for t in tools] == ["add", "divide"]
    assert all({"name", "description", "inputSchema"} <= set(t) for t in tools)
    ok = c.request("tools/call", {"name": "add", "arguments": {"a": 2, "b": 3}})["result"]
    assert ok == {"content": [{"type": "text", "text": "5"}], "isError": False}
    bad = c.request("tools/call", {"name": "divide", "arguments": {"a": 1, "b": 0}})
    assert bad["result"]["isError"] is True and "error" not in bad     # failure is a result
    assert c.request("tools/call", {"name": "nope"})["error"]["code"] == -32602
    assert c.request("resources/list")["error"]["code"] == -32601
    logs = c.close()
    assert "server saw" in logs                          # logs went to stderr, not stdout
    print("tools:", [t["name"] for t in tools], "| add(2,3) ->", ok["content"][0]["text"])
    print("mcp_stdio: all checks passed")
