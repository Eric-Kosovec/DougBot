import time


class LRUCache:

    class _Node:

        def __init__(self, value):
            self.value = value
            self.time_used = time.time()

        def update_time(self):
            self.time_used = time.time()

    def __init__(self, limit):
        self._cache = {}
        self._limit = limit

    def insert(self, key, value):
        if self.size() >= self._limit:
            self._evict()
        self._cache[key] = self._Node(value)

    def get(self, key):
        try:
            node = self._cache[key]
            node.update_time()
            return node.value
        except KeyError:
            return None

    def remove(self, key):
        value = None
        if key in self._cache:
            value = self._cache[key]
            del self._cache[key]
        return value

    def size(self):
        return len(self._cache)

    def _evict(self):
        lru_key = None
        lru_time = None

        for key in self._cache.keys():
            if lru_key is None or self._cache[key].time_used < lru_time:
                lru_time = self._cache[key].time_used
                lru_key = key

        self.remove(lru_key)

    def __getitem__(self, item):
        return self.get(item)

    def __len__(self):
        return self.size()
