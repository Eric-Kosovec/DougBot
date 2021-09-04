from symspellpy.symspellpy import SymSpell
from symspellpy.symspellpy import Verbosity


class Autocorrect:

    def __init__(self, words=None, max_edit_distance=2):
        self._symspell = SymSpell()
        self._max_edit_distance = max_edit_distance
        if words is not None:
            self.add_words(words)

    def add_word(self, word):
        if word is not None:
            self._symspell.create_dictionary_entry(word, 1)

    def add_words(self, words):
        if words is not None:
            self._symspell.create_dictionary(words)

    def delete_word(self, word):
        if word is not None:
            self._symspell.delete_dictionary_entry(word)

    def correct(self, bad_word):
        if bad_word is None:
            return ''
        return self._symspell.lookup(bad_word, Verbosity.TOP,
                                     max_edit_distance=self._max_edit_distance, include_unknown=True)[0].term

    def predictions(self, bad_word):
        if bad_word is None:
            return []
        return self._symspell.lookup(bad_word, Verbosity.CLOSEST,
                                     max_edit_distance=self._max_edit_distance, include_unknown=True)
