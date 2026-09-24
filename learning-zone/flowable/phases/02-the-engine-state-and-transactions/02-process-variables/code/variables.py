"""Process variables & scope: a parent-chained variable store.

Real engines don't keep one flat dict per instance. Each execution (token) is a
scope with a parent; reads walk up the chain, writes go to the scope that
declares the variable (or the root if none does), and set_local pins a variable
to the current branch. This is exactly Flowable's VariableScope semantics.

Run: python3 variables.py
"""


class Scope:
    def __init__(self, name, parent=None):
        self.name, self.parent, self.vars = name, parent, {}

    # read: nearest declaration wins, walking up the chain
    def get(self, key):
        scope = self
        while scope:
            if key in scope.vars:
                return scope.vars[key]
            scope = scope.parent
        raise KeyError(key)

    # write: update wherever the variable is declared; else declare at the root
    def set(self, key, value):
        scope = self
        while scope:
            if key in scope.vars:
                scope.vars[key] = value
                return
            if scope.parent is None:
                scope.vars[key] = value       # new variable -> process instance level
                return
            scope = scope.parent

    # write, but pinned to this branch — invisible to siblings, dies with the scope
    def set_local(self, key, value):
        self.vars[key] = value

    def visible(self):
        out, scope = {}, self
        while scope:
            for k, v in scope.vars.items():
                out.setdefault(k, v)
            scope = scope.parent
        return out


if __name__ == "__main__":
    # A loan instance forks into two parallel branches (credit + KYC).
    instance = Scope("instance")
    instance.set("applicant", "meera")
    instance.set("amount", 500_000)

    credit = Scope("credit-branch", parent=instance)
    kyc = Scope("kyc-branch", parent=instance)

    # Both branches read instance-level data through the chain:
    assert credit.get("applicant") == "meera"
    assert kyc.get("amount") == 500_000

    # Branch-local working state stays local — no cross-branch clobbering:
    credit.set_local("attempt", 1)
    kyc.set_local("attempt", 3)
    assert credit.get("attempt") == 1 and kyc.get("attempt") == 3

    # An undeclared name set from a branch lands at the instance root,
    # so it survives after the branch scope is destroyed at the join:
    credit.set("score", 720)
    assert instance.get("score") == 720

    # THE classic bug: both branches "return" via the same instance-level name.
    credit.set("result", "credit-ok")
    kyc.set("result", "kyc-ok")               # silently overwrites the sibling's write
    print("instance sees result =", instance.get("result"), " <- last writer won")

    # The fix: distinct names (or keep working state local until the join):
    credit.set("credit_result", "ok")
    kyc.set("kyc_result", "ok")
    print("instance variables:", instance.visible())
