"""The job executor: timers, retries, and async work as rows in a table.

A job is a row: what to run, when it's due, how many retries remain, and a lock
so that in a cluster exactly one node runs it. The executor is a loop:
acquire due jobs (by locking them), execute, and on failure reschedule with
backoff until retries run out -> dead letter.

Uses a fake clock so the demo runs instantly. Run: python3 job_executor.py
"""
import itertools
from dataclasses import dataclass, field

RETRIES = 3
BACKOFF = [10, 60, 300]          # seconds until next attempt, per failure
LOCK_SECONDS = 30


@dataclass
class Job:
    id: int
    kind: str                    # "timer" | "async"
    handler: object
    due: float                   # epoch seconds when the job may run
    retries: int = RETRIES
    locked_by: str = None
    lock_until: float = 0.0


@dataclass
class JobStore:
    clock: object                # callable -> now (fake in the demo)
    jobs: list = field(default_factory=list)
    dead: list = field(default_factory=list)
    _seq: object = field(default_factory=lambda: itertools.count(1))

    def add(self, kind, handler, delay=0.0):
        job = Job(next(self._seq), kind, handler, due=self.clock() + delay)
        self.jobs.append(job)
        return job.id

    def acquire(self, node, limit=10):
        """The cluster-safety core. In SQL this is one guarded UPDATE:
        UPDATE job SET locked_by=?, lock_until=? WHERE due<=now
          AND (locked_by IS NULL OR lock_until<now) LIMIT ?"""
        now, got = self.clock(), []
        for job in self.jobs:
            if len(got) == limit:
                break
            if job.due <= now and (job.locked_by is None or job.lock_until < now):
                job.locked_by, job.lock_until = node, now + LOCK_SECONDS
                got.append(job)
        return got


def run_once(store, node):
    """One executor tick on one node: acquire, execute, settle."""
    for job in store.acquire(node):
        try:
            job.handler()
            store.jobs.remove(job)                      # success: job is gone
            print(f"  [{node}] job {job.id} ({job.kind}) done")
        except Exception as e:
            job.locked_by = None
            job.retries -= 1
            if job.retries == 0:
                store.jobs.remove(job)
                store.dead.append(job)                  # dead letter: needs a human
                print(f"  [{node}] job {job.id} DEAD-LETTERED: {e}")
            else:
                backoff = BACKOFF[RETRIES - job.retries - 1]
                job.due = store.clock() + backoff
                print(f"  [{node}] job {job.id} failed ({e}); "
                      f"retry in {backoff}s ({job.retries} left)")


if __name__ == "__main__":
    now = [1000.0]
    store = JobStore(clock=lambda: now[0])

    # a timer: "send the offer-expiry reminder in 3 days" (here: 300 fake seconds)
    store.add("timer", lambda: print("      -> reminder sent"), delay=300)

    # an async continuation whose external call fails twice, then succeeds
    attempts = [0]
    def flaky_bureau_call():
        attempts[0] += 1
        if attempts[0] < 3:
            raise RuntimeError(f"bureau 502 (attempt {attempts[0]})")
        print("      -> bureau responded, token advances")
    store.add("async", flaky_bureau_call)

    # an async job that always fails -> dead letter
    store.add("async", lambda: (_ for _ in ()).throw(RuntimeError("bad config")))

    print("t=0: both async jobs due, timer is not")
    run_once(store, "node-A")
    run_once(store, "node-B")        # B finds nothing unlocked & due — no double-run

    for step in (10, 60, 300):
        now[0] += step
        print(f"t=+{int(now[0] - 1000)}s:")
        run_once(store, "node-B")

    print("dead letters:", [(j.id, j.kind) for j in store.dead])
    assert not store.jobs and len(store.dead) == 1
