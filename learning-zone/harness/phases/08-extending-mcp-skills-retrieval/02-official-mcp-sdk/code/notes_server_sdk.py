# needs: pip install mcp   (no API key). Checked against mcp 2.2.0 and 2.3.0 on 2026-10-02.
# In mcp 1.x the import is: from mcp.server.fastmcp import FastMCP
"""A notes MCP server on the official Python SDK. Notes persist in a JSON file.

Run:  python3 code/notes_server_sdk.py            (stdio, for an MCP client)
"""
import json
import os
from pathlib import Path

from mcp.server import MCPServer

NOTES_FILE = Path(os.environ.get("NOTES_FILE", "notes.json"))
mcp = MCPServer("notes", instructions="Save short notes and search them.")


def _load() -> list[str]:
    return json.loads(NOTES_FILE.read_text()) if NOTES_FILE.exists() else []


@mcp.tool()
def remember(note: str) -> str:
    """Save a note to disk."""
    notes = _load()
    notes.append(note)
    NOTES_FILE.write_text(json.dumps(notes))
    return f"saved ({len(notes)} notes)"


@mcp.tool()
def recall(query: str, limit: int = 3) -> list[str]:
    """Return saved notes that share a word with the query."""
    words = set(query.lower().split())
    return [n for n in _load() if words & set(n.lower().split())][:limit]


@mcp.resource("notes://all")
def all_notes() -> str:
    """Every saved note, one per line."""
    return "\n".join(_load())


if __name__ == "__main__":
    mcp.run()                    # stdio by default; mcp.run("streamable-http") serves HTTP
