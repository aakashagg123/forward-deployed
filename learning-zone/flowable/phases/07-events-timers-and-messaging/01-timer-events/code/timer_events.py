"""Timer events: ISO-8601 in the model, jobs underneath.

Three timer shapes BPMN gives you, all reduced here to "a job with a due time"
(Phase 2, lesson 04):
  duration  PT4H / P30D      fire once, N seconds after arming
  date      2026-08-01T09:00 fire once, at an absolute instant
  cycle     R3/P1D           fire N times, one interval apart

Fake clock, so the demo runs instantly. Run: python3 timer_events.py
"""
import re
from dataclasses import dataclass, field

DUR = re.compile(
    r"^P(?:(?P<d>\d+)D)?(?:T(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+)S)?)?$")


def parse_duration(text):
    """P3D, PT4H, PT30M, P1DT12H ... -> seconds."""
    m = DUR.match(text)
    assert m and text != "P", f"bad ISO-8601 duration: {text!r}"
    g = {k: int(v or 0) for k, v in m.groupdict().items()}
    return ((g["d"] * 24 + g["h"]) * 60 + g["m"]) * 60 + g["s"]


def parse_cycle(text):
    """R3/P1D -> (3 repetitions, 86400 s apart). R/P1D -> unbounded."""
    reps, _, dur = text.partition("/")
    assert reps.startswith("R") and dur, f"bad ISO-8601 cycle: {text!r}"
    return (int(reps[1:]) if len(reps) > 1 else None), parse_duration(dur)


@dataclass
class Timer:
    fire_at: float
    action: object            # callable(now) -> None
    repeats_left: object = 1  # None = unbounded cycle
    interval: float = 0.0
    cancelled: bool = False


@dataclass
class TimerService:
    clock: object
    timers: list = field(default_factory=list)

    def after(self, iso_duration, action):
        t = Timer(self.clock() + parse_duration(iso_duration), action)
        self.timers.append(t)
        return t

    def cycle(self, iso_cycle, action):
        reps, interval = parse_cycle(iso_cycle)
        t = Timer(self.clock() + interval, action, reps, interval)
        self.timers.append(t)
        return t

    def tick(self):
        """One executor pass: fire everything due (Phase 2's acquire loop,
        minus the locking — cluster safety is identical to job acquisition)."""
        now = self.clock()
        for t in list(self.timers):
            if t.cancelled or t.fire_at > now:
                continue
            t.action(now)
            if t.repeats_left is not None:
                t.repeats_left -= 1
            if t.repeats_left == 0:
                self.timers.remove(t)
            else:
                t.fire_at += t.interval


if __name__ == "__main__":
    DAY = 86400.0
    now = [0.0]
    svc = TimerService(clock=lambda: now[0])

    # The capstone's offer step: 3 daily reminders, hard expiry at day 30.
    state = {"offer": "open"}

    reminders = svc.cycle("R3/P1D", lambda t: print(f"  day {t/DAY:>4.0f}: reminder sent"))

    def expire(t):
        state["offer"] = "expired"
        reminders.cancelled = True            # interrupting boundary: cancel siblings
        print(f"  day {t/DAY:>4.0f}: offer EXPIRED — token leaves acceptOffer")
    expiry = svc.after("P30D", expire)

    def accept_offer_completed():
        """What task completion does to armed boundary timers: disarms them."""
        expiry.cancelled = True
        reminders.cancelled = True

    for day in (1, 2, 3, 10, 30, 31):
        now[0] = day * DAY
        svc.tick()

    assert state["offer"] == "expired" and not svc.timers
    print("timers drained; sanity:",
          f'PT4H={parse_duration("PT4H")}s', f'P1DT12H={parse_duration("P1DT12H")}s')
