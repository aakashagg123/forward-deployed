"""A tenant-scoped cache that can't cross-contaminate. Run:  python3 isolation.py"""
import hashlib


class TenantCache:
    def __init__(self):
        self._store = {}

    def _key(self, tenant, query):
        return hashlib.sha256(f"{tenant}::{query}".encode()).hexdigest()

    def get(self, tenant, query):
        return self._store.get(self._key(tenant, query))

    def set(self, tenant, query, value):
        self._store[self._key(tenant, query)] = value


if __name__ == "__main__":
    c = TenantCache()
    c.set("tenantA", "secret report", "A's data")
    print("B sees:", c.get("tenantB", "secret report"))   # None
    print("A sees:", c.get("tenantA", "secret report"))   # A's data
