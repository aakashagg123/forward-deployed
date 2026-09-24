"""Message events: correlating the outside world to the right instance.

A message catch is a wait state with a name tag: the token subscribes to
(message name, correlation key) and sleeps. Delivery is a lookup — the engine
finds THE subscription matching both, injects the payload as variables, and
wakes that one token. No match = a correlation failure you must decide about.

Run: python3 message_events.py
"""
from dataclasses import dataclass, field


class CorrelationError(Exception):
    pass


@dataclass
class Subscription:
    message: str            # e.g. "bureauCallback"
    key: str                # business key, e.g. application id
    wake: object            # callable(payload) -> None


@dataclass
class MessageBroker:
    subs: list = field(default_factory=list)

    def subscribe(self, message, key, wake):
        assert not any(s.message == message and s.key == key for s in self.subs), \
            f"duplicate subscription {message}/{key} — correlation would be ambiguous"
        self.subs.append(Subscription(message, key, wake))

    def correlate(self, message, key, payload):
        hits = [s for s in self.subs if s.message == message and s.key == key]
        if not hits:
            raise CorrelationError(
                f"no instance waiting for {message!r} with key {key!r} "
                f"(late? already completed? wrong key?)")
        (sub,) = hits                       # unique by construction
        self.subs.remove(sub)
        sub.wake(payload)


@dataclass
class LoanInstance:
    app_id: str
    state: str = "started"
    variables: dict = field(default_factory=dict)

    def wait_for_bureau(self, broker):
        self.state = "waiting-for-bureau"   # token asleep at the message catch
        broker.subscribe("bureauCallback", self.app_id, self._bureau_arrived)

    def _bureau_arrived(self, payload):
        self.variables.update(payload)      # payload -> process variables
        self.state = "deciding"             # token moves on
        print(f"  {self.app_id}: woke with score={payload['score']}")


if __name__ == "__main__":
    broker = MessageBroker()
    a = LoanInstance("APP-001")
    b = LoanInstance("APP-002")
    a.wait_for_bureau(broker)
    b.wait_for_bureau(broker)

    # A second instance trying to wait on the SAME key is caught at arming
    # time — two matches would make every future delivery ambiguous:
    c = LoanInstance("APP-001")
    try:
        c.wait_for_bureau(broker)
    except AssertionError as e:
        print("  ambiguity :", e)

    # The bureau answers for APP-002 first — correlation, not arrival order,
    # picks the instance:
    broker.correlate("bureauCallback", "APP-002", {"score": 731})
    assert b.state == "deciding" and a.state == "waiting-for-bureau"

    broker.correlate("bureauCallback", "APP-001", {"score": 688})
    assert a.state == "deciding"

    # A late/duplicate callback has nobody waiting — surface it, don't drop it:
    try:
        broker.correlate("bureauCallback", "APP-001", {"score": 688})
    except CorrelationError as e:
        print("  duplicate :", e)
