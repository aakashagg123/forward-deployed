"""A memory MCP server on the official Python SDK.

Requires:  pip install mcp   (then register with: claude mcp add memory -- python sdk_server.py)
This file is illustrative of the SDK shape; compare to lesson-02 server.py.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("memory")

_STORE: list[str] = []


@mcp.tool()
def remember(fact: str) -> str:
    """Save a durable fact."""
    _STORE.append(fact)
    return "remembered"


@mcp.tool()
def recall(query: str, k: int = 3) -> list[str]:
    """Retrieve relevant facts."""
    return [f for f in _STORE if any(w in f for w in query.split())][:k]


if __name__ == "__main__":
    mcp.run()                    # serves over stdio by default
