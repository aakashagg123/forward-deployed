"""The task lifecycle: a small state machine with sharp transition rules.

A user task is more than "waiting": it moves through states, and each
transition has preconditions the engine enforces so two people can't do the
same work twice.

  CREATED --claim--> CLAIMED --complete--> COMPLETED
     |                  |
     |                  +--unclaim--> CREATED
     |                  +--delegate--> DELEGATED --resolve--> CLAIMED (back w/ owner)
     +--complete--> X  (refused: unclaimed group tasks have no accountable person)

Run: python3 task_lifecycle.py
"""
from dataclasses import dataclass, field


class TransitionError(Exception):
    pass


@dataclass
class Task:
    name: str
    candidate_groups: set = field(default_factory=set)
    assignee: str = None
    owner: str = None            # set when delegated: who remains accountable
    state: str = "CREATED"
    log: list = field(default_factory=list)

    def _check(self, ok, msg):
        if not ok:
            raise TransitionError(f"{self.name}: {msg}")

    def visible_to(self, user, groups):
        return self.assignee == user or bool(self.candidate_groups & set(groups))

    def claim(self, user, groups):
        self._check(self.state == "CREATED", f"cannot claim in state {self.state}"
                    + (f" (held by {self.assignee})" if self.assignee else ""))
        self._check(self.visible_to(user, groups),
                    f"{user} is not a candidate ({self.candidate_groups})")
        self.assignee, self.state = user, "CLAIMED"
        self.log.append(f"claimed by {user}")

    def unclaim(self):
        self._check(self.state == "CLAIMED", "nothing to unclaim")
        self.log.append(f"unclaimed by {self.assignee}")
        self.assignee, self.state = None, "CREATED"   # back to the group pool

    def delegate(self, to_user):
        self._check(self.state == "CLAIMED", "only a claimed task can be delegated")
        self.owner, self.assignee, self.state = self.assignee, to_user, "DELEGATED"
        self.log.append(f"{self.owner} delegated to {to_user}")

    def resolve(self, user):
        self._check(self.state == "DELEGATED" and user == self.assignee,
                    "only the delegate resolves")
        self.assignee, self.owner, self.state = self.owner, None, "CLAIMED"
        self.log.append(f"resolved by {user}; back with {self.assignee}")

    def complete(self, user):
        self._check(self.state == "CLAIMED", f"cannot complete in state {self.state}")
        self._check(user == self.assignee, f"{user} is not the assignee")
        self.state = "COMPLETED"
        self.log.append(f"completed by {user}")


if __name__ == "__main__":
    review = Task("Manual credit review", candidate_groups={"credit-ops"})

    # Claim race: first claim wins, second is refused — this is the guarantee
    # that makes candidate groups safe for maker-checker work.
    review.claim("asha", ["credit-ops"])
    for attempt in [("ravi", ["credit-ops"]), ("asha-again", ["credit-ops"])]:
        try:
            review.claim(*attempt)
        except TransitionError as e:
            print("refused :", e)

    # Completing without being the assignee is refused too:
    try:
        review.complete("ravi")
    except TransitionError as e:
        print("refused :", e)

    # Delegation: asha asks a senior to look, stays accountable, gets it back.
    review.delegate("meera")
    review.resolve("meera")
    review.complete("asha")
    print("\naudit trail:")
    for line in review.log:
        print("  -", line)
