# needs: pip install mcp   (no API key). Checked against mcp 2.2.0 and 2.3.0 on 2026-10-02.
"""Drive notes_server_sdk.py with the SDK client and check the result.

Run:  python3 code/notes_client_sdk.py
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

from mcp import Client, StdioServerParameters

SERVER = str(Path(__file__).with_name("notes_server_sdk.py"))


async def main(notes_file):
    params = StdioServerParameters(command=sys.executable, args=[SERVER],
                                   env={**os.environ, "NOTES_FILE": notes_file})
    async with Client(params) as client:
        names = [t.name for t in (await client.list_tools()).tools]
        assert names == ["remember", "recall"], names
        await client.call_tool("remember", {"note": "deploys happen on tuesday"})
        hit = await client.call_tool("recall", {"query": "tuesday"})
        assert "deploys happen on tuesday" in hit.content[0].text
    # A second server process reads the same file, so the note survived the restart.
    async with Client(params) as client:
        again = await client.call_tool("recall", {"query": "deploys"})
        assert "tuesday" in again.content[0].text
    print("tools:", names, "| note persisted across two server processes")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        asyncio.run(main(str(Path(d) / "notes.json")))
