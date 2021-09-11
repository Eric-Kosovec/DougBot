import time

from collections import UserDict


class LRUCache(UserDict):

    class _Node:

        def __init__(self, value):
            self.value = value
            self.time_used = time.time()

        async def update_time_async(self):
            self.update_time()

        def update_time(self):
            self.time_used = time.time()

        def __repr__(self):
            return f'{self.value.__repr__()}'

    def __init__(self, limit):
        super().__init__()
        self._limit = limit

    def __setitem__(self, key, value):
        while len(self.data) >= self._limit:
            self._evict()
        self.data[key] = self._Node(value)

    def __getitem__(self, key):
        try:
            node = self.data[key]
            node.update_time()
            return node.value
        except KeyError:
            return None

    def __delitem__(self, key):
        self.data.pop(key)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f'{type(self).__name__}({super().__repr__()})'

    def __str__(self):
        return self.data.__str__()

    async def insert(self, key, value):
        while len(self.data) >= self._limit:
            await self._evict_async()
        self.data[key] = self._Node(value)

    async def get(self, key):
        return self[key]

    async def remove(self, key):
        del self[key]

    async def _evict_async(self):
        self._evict()

    def _evict(self):
        lru_key = None
        lru_time = None

        for key in self.data.keys():
            if lru_key is None or self.data[key].time_used < lru_time:
                lru_time = self.data[key].time_used
                lru_key = key

        self.data.pop(lru_key)
