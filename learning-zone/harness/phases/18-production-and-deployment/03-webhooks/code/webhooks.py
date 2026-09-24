"""A typed webhook event router. Run:  python3 webhooks.py

In production: verify the webhook signature before dispatch, and treat every payload
field as untrusted data (Phase 17).
"""


class EventRouter:
    def __init__(self):
        self.handlers = {}

    def on(self, event_type):
        def deco(fn):
            self.handlers[event_type] = fn
            return fn
        return deco

    def dispatch(self, event):
        t = event.get("type")
        handler = self.handlers.get(t)
        if not handler:
            return f"ignored: no handler for {t!r}"
        return handler(event)


if __name__ == "__main__":
    router = EventRouter()

    @router.on("ci_failure")
    def fix_ci(e):
        return f"investigating failure in {e['run']}"

    @router.on("pr_comment")
    def reply(e):
        return f"considering comment: {e['body'][:20]}"

    print(router.dispatch({"type": "ci_failure", "run": "build #42"}))
    print(router.dispatch({"type": "pr_comment", "body": "please add tests here"}))
    print(router.dispatch({"type": "push"}))
