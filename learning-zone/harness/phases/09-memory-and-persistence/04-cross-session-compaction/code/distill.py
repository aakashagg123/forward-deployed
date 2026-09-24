"""Distill a finished session transcript into durable memory entries.

`extract` is a model call in production; here a simple heuristic. Run: python3 distill.py
"""


def distill(transcript, remember):
    lessons = []
    for msg in transcript:
        text = msg.get("content", "")
        if isinstance(text, str) and ("fix:" in text.lower() or "lesson:" in text.lower()):
            lessons.append(text.strip())
    for lesson in lessons:
        remember(lesson, tags=["lesson"])
    return f"distilled {len(lessons)} lesson(s)"


if __name__ == "__main__":
    saved = []
    transcript = [
        {"role": "assistant", "content": "Fix: the flaky test needs a 200ms wait."},
        {"role": "assistant", "content": "Did some refactoring."},
    ]
    print(distill(transcript, remember=lambda f, tags: saved.append(f)))
    print(saved)
