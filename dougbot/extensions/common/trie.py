
class Trie:

    _END_STRING = 'END'

    def __init__(self):
        self._head = {}
        self._count = 0

    def add_all(self, strings):
        for string in strings:
            self.add(string)

    def add(self, string):
        curr_trie = self._head
        for c in string:
            if c not in curr_trie:
                curr_trie[c] = {}
            curr_trie = curr_trie[c]
        curr_trie[Trie._END_STRING] = True
        self._count += 1

    def delete(self, string):
        if len(self) == 0:
            return False

        stack = []
        curr_trie = self._head
        for c in string:
            if c not in curr_trie:
                return False
            stack.append(curr_trie)
            curr_trie = curr_trie[c]

        if not self._has_end_string(curr_trie):
            return False

        curr_trie[self._END_STRING] = False

        if len(curr_trie) == 1:
            if self._head == curr_trie:
                self._head.clear()
            else:
                del curr_trie

        for c in reversed(string):
            previous_trie = stack.pop()
            if len(previous_trie) >= 1:
                del previous_trie[c]
                # More letters in the subtrie, so can't delete any more up the trie
                if len(previous_trie) >= 1:
                    break

        self._count -= 1
        return True

    def suffixes(self, string):
        if len(self) == 0:
            return []

        suffixes = []
        frontier = [("", self._trie_after_last_match(string))]
        while len(frontier) > 0:
            suffix, curr_trie = frontier.pop()
            for c in curr_trie.keys():
                if c != self._END_STRING:
                    frontier.append((suffix + c, curr_trie[c]))
                    if self._has_end_string(curr_trie[c]):
                        suffixes.append(suffix + c)

        return suffixes

    def contains(self, string):
        if len(self) == 0:
            return False

        curr_trie = self._head
        for c in string:
            if c not in curr_trie:
                return False
            curr_trie = curr_trie[c]

        return self._has_end_string(curr_trie)

    def __contains__(self, item):
        return self.contains(item)

    def __len__(self):
        return self._count

    def _has_end_string(self, trie):
        if trie is None:
            return False
        return self._END_STRING in trie and trie[self._END_STRING]

    def _trie_after_last_match(self, string):
        curr_trie = self._head
        for c in string:
            if c not in curr_trie:
                break
            curr_trie = curr_trie[c]
        return curr_trie

