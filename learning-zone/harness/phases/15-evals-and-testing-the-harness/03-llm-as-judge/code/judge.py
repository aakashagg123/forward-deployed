"""LLM-as-judge rubric scorer (model call abstracted). Run:  python3 judge.py"""
import json

RUBRIC = """Score the answer 0-5 on:
- correctness (is it right?)
- completeness (does it cover the question?)
Return JSON: {"score": <0-5>, "reason": "<one line>"}."""


def judge(output, question, call_model, rubric=RUBRIC):
    prompt = f"{rubric}\n\nQuestion: {question}\nAnswer: {output}"
    return json.loads(call_model(prompt))      # model returns the JSON verdict


def normalize(verdict, scale=5):
    return verdict["score"] / scale            # 0..1 for aggregation


if __name__ == "__main__":
    fake_model = lambda p: '{"score": 4, "reason": "correct but missing an edge case"}'
    v = judge("Paris is the capital of France.", "Capital of France?", fake_model)
    print(v, "->", normalize(v))
