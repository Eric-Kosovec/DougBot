from collections import deque


class Queue:
    def __init__(self):
        self.q = deque()

    def enqueue(self, element):
        self.q.append(element)

    def dequeue(self):
        return self.q.popleft()

    def remove(self, element):
        self.q.remove(element)

    def clear(self):
        self.q.clear()

    def max_length(self):
        return self.q.maxlen

    def size(self):
        return len(self.q)

    def is_empty(self):
        return self.size() == 0
