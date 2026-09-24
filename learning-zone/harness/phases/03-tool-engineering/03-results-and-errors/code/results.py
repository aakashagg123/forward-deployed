"""Wrap tool outcomes into tool_result blocks (id + content + is_error) with capping.

Run:  python3 results.py
"""
MAX_RESULT_CHARS = 4000


def ok(tool_use_id, content):
    return _block(tool_use_id, str(content), is_error=False)


def err(tool_use_id, message):
    return _block(tool_use_id, f"error: {message}", is_error=True)


def _block(tool_use_id, content, is_error):
    if len(content) > MAX_RESULT_CHARS:
        head = content[:MAX_RESULT_CHARS]
        content = f"{head}\n…[truncated {len(content) - MAX_RESULT_CHARS} chars]"
    return {"type": "tool_result", "tool_use_id": tool_use_id,
            "content": content, "is_error": is_error}


if __name__ == "__main__":
    print(ok("t1", 42))
    print(err("t2", "file not found"))
    print(_block("t3", "x" * 5000, False)["content"][-30:])
