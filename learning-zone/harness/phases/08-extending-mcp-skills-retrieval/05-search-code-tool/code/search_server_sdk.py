# needs: pip install mcp   (no API key). Checked against mcp 2.2.0 and 2.3.0 on 2026-10-02.
"""Expose search_code as an MCP tool. Index the directory in REPO_ROOT (default: .).

Run:  python3 code/search_server_sdk.py     (stdio server)
Check: python3 code/search_server_sdk.py --check
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retrieval_tool import CodeSearch, TOOL_SPEC  # noqa: E402
from mcp.server import MCPServer  # noqa: E402

search = CodeSearch()
search.index_dir(os.environ.get("REPO_ROOT", "."))
mcp = MCPServer("code-search")


@mcp.tool(name=TOOL_SPEC["name"], description=TOOL_SPEC["description"])
def search_code(query: str, k: int = 3) -> str:
    hits = search.search_code(query, k)
    return "\n".join(hits) or "no matches"


async def check():
    from mcp import Client
    global search
    with tempfile.TemporaryDirectory() as d:
        Path(d, "auth.py").write_text("def login_user(n):\n    'authenticate the user'\n    return n\n")
        search = CodeSearch()
        search.index_dir(d)
        async with Client(mcp) as client:
            assert [t.name for t in (await client.list_tools()).tools] == ["search_code"]
            hit = await client.call_tool("search_code", {"query": "authenticate user"})
            assert hit.content[0].text == "auth.py:1  login_user", hit.content
    print("search_server_sdk: in-memory client check passed")


if __name__ == "__main__":
    asyncio.run(check()) if "--check" in sys.argv else mcp.run()
