from collections import deque


class Queue:

    def __init__(self, queue_list=None):
        if queue_list is None:
            self._q = deque()
        else:
            self._q = deque(queue_list)

    def enqueue(self, element):
        self._q.append(element)

    def dequeue(self):
        return self._q.popleft()

    def remove(self, element):
        self._q.remove(element)

    def clear(self):
        self._q.clear()

    def is_empty(self):
        return len(self) == 0

    def __len__(self):
        return len(self._q)
