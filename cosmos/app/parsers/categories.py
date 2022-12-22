from typing import Dict
from collections import defaultdict
from app.data.presets import presets, Preset
from strsimpy.normalized_levenshtein import NormalizedLevenshtein

import re
from typing import Set

import unicodedata

levenshtein = NormalizedLevenshtein()


class CategoryLookup:
    """Index for searching categories."""
    NAME_SIMILARITY_THRESHOLD = 0.33
    TERM_SIMILARITY_THRESHOLD = 0.33


    def _clean(self, s: str) -> str:
        return unicodedata.normalize("NFD", s).lower().strip()

    def __init__(self, category: Dict[str, Preset]) -> None:
        self.categories = category
        # Fill in a term -> category index
        self._name_idx: Dict[str, Set[str]] = defaultdict(set)
        self._term_idx: Dict[str, Set[str]] = defaultdict(set)
        self._tag_value_idx: Dict[str, Set[str]] = defaultdict(set)
        for k, v in self.categories.items():
            name = self._clean(v.name)
            self._name_idx[name].add(k)
            if name.endswith(' feature'):
                self._name_idx[re.sub(' feature$', '', name)].add(k)
            for alias in v.aliases:
                self._name_idx[self._clean(alias)].add(k)
            # Terms
            for term in v.terms:
                self._term_idx[self._clean(term)].add(k)
            # tags
            for value in v.tags.values():
                value = re.sub("[_]", " ", value)
                if value not in {'yes', 'no', '*'}:
                    self._tag_value_idx[self._clean(value)].add(k)

    def _similar_names(self, query) -> set[str]:
        matches = set()
        for k, v in self._name_idx.items():
            d = levenshtein.distance(query, k)
            print(d)
            if d < self.NAME_SIMILARITY_THRESHOLD:
                matches.update(v)
        return matches

    def _similar_terms(self, query) -> set[str]:
        matches = set()
        for k, v in self._term_idx.items():
            d = levenshtein.distance(query, k)
            print(d)
            if d < self.TERM_SIMILARITY_THRESHOLD:
                matches.update(v)
        return matches

    def _name_match(self, words) -> set[str]:
        n_words = len(words)
        for n in range(n_words, 0, -1):
            for i in range(n_words - n + 1):
                needle = ' '.join(words[i:i+n])
                if cats := self._name_idx.get(needle, set()):
                    return cats
        return set()

    def _term_match(self, words) -> set[str]:
        n_words = len(words)
        for n in range(n_words, 0, -1):
            for i in range(n_words - n + 1):
                needle = ' '.join(words[i:i+n])
                if cats := self._term_idx.get(needle, set()):
                    return cats
        return set()

    def _tag_value_match(self, words) -> set[str]:
        n_words = len(words)
        for n in range(n_words, 0, -1):
            for i in range(n_words - n + 1):
                needle = ' '.join(words[i:i+n])
                if cats := self._tag_value_idx.get(needle, set()):
                    return cats
        return set()

    def __call__(self, query) -> list[Preset]:
        """Retrieve categories matching the query.

        1. subset of words matches names or aliases
        2. subset of words matches terms
        3. subset of words matches tag values
        4. complete query is similar to names or aliases by normalized Levenshtein distance
        5. complete query is similar to terms by normalized Levenshtein distance

        These criteria are simmilar to those used in the ID editor to search for presets.
        https://github.com/openstreetmap/iD/blob/3dde091fdd3f8c5e54abd9923d642e67adb05064/modules/presets/collection.js#L137

        """
        # TODO: use a real tokenizer
        # TODO: use a real stemmer
        # TODO: use a real stopword list

        # want to match some subset of words in the query
        # will match the longest subset first
        query = self._clean(query)
        words = query.split(' ')
        if matches := self._name_match(words):
            return [self.categories[c] for c in matches]
        if matches := self._term_match(words):
            return [self.categories[c] for c in matches]
        if matches := self._tag_value_match(words):
            return [self.categories[c] for c in matches]
        if matches := self._similar_names(query.lower()):
            return [self.categories[c] for c in matches]
        if matches := self._similar_terms(query.lower()):
            return [self.categories[c] for c in matches]
        else:
            return []

category_lookup = CategoryLookup(presets)
"""Category lookup index."""
