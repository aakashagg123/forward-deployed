"""A deferred-loading tool registry: names up front, schemas on demand. Run: python3 deferred.py"""


class DeferredRegistry:
    def __init__(self):
        self._loaders = {}        # name -> () -> full schema
        self._cache = {}

    def register(self, name, loader):
        self._loaders[name] = loader      # cheap: name + a thunk

    def index(self):
        return list(self._loaders)        # names only — always in context

    def load(self, name):
        if name not in self._cache:
            self._cache[name] = self._loaders[name]()   # fetch full schema on demand
        return self._cache[name]

    def search(self, term):
        return [n for n in self._loaders if term in n]


if __name__ == "__main__":
    reg = DeferredRegistry()
    reg.register("github_create_pr",
                 lambda: {"name": "github_create_pr", "input_schema": {"...": "big"}})
    reg.register("github_list_issues",
                 lambda: {"name": "github_list_issues", "input_schema": {}})
    print("index:", reg.index())
    print("search pr:", reg.search("pr"))
    print("load:", reg.load("github_create_pr"))
