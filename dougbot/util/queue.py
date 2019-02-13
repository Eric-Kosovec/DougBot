from collections import deque


class Queue:

    def __init__(self):
        self.items = deque()

    async def put(self, item):
        if item is not None:
            self.items.append(item)

    async def get(self):
        if len(self.items) <= 0:
            return None
        return self.items.popleft()

    async def clear(self):
        self.items.clear()

    async def empty(self):
        return len(self.items) <= 0

    def __len__(self):
        return len(self.items)
