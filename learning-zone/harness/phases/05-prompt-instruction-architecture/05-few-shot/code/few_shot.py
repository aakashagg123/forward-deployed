"""Top-k few-shot example selection + formatting. Lexical overlap stands in for
embeddings (Phase 13). Run:  python3 few_shot.py
"""


def select(examples, query, k=2):
    def overlap(ex):
        a, b = set(ex["input"].lower().split()), set(query.lower().split())
        return len(a & b)
    return sorted(examples, key=overlap, reverse=True)[:k]


def format_fewshot(examples, query):
    shots = "\n\n".join(f"Input: {e['input']}\nOutput: {e['output']}" for e in examples)
    return f"{shots}\n\nInput: {query}\nOutput:"


if __name__ == "__main__":
    ex = [{"input": "add user route", "output": "POST /users"},
          {"input": "delete a product", "output": "DELETE /products/:id"},
          {"input": "list orders", "output": "GET /orders"}]
    picked = select(ex, "add product route", k=2)
    print(format_fewshot(picked, "add product route"))
