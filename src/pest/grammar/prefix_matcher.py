"""An efficient string prefix matcher."""

from collections.abc import Sequence
from typing import Any


class PrefixMatcher:
    """A trie-based string prefix matcher.

    Args:
        prefix: A sequence of prefixes.
    """

    def __init__(self, prefixes: Sequence[str]) -> None:
        self.trie: dict[str, Any] = {}
        for word in prefixes:
            node = self.trie
            for ch in word:
                node = node.setdefault(ch, {})
            node["$"] = True  # end of word marker

    def match_longest(self, s: str, start: int = 0) -> tuple[str, int, int] | None:
        """Return the longest prefix match in `s` starting at `start`.

        Returns:
            A tuple: (matched_prefix, matched_length, end_index)
            or None if no match is found.
        """
        node = self.trie
        longest: tuple[str, int, int] | None = None
        i = start

        while i < len(s) and s[i] in node:
            node = node[s[i]]
            i += 1
            if "$" in node:
                longest = (s[start:i], i - start, i)

        return longest


# TODO: unit tests
# TODO: when does this start to be more efficient than a simple loop with startswith?
# TODO: different sentinel "end of word marker"
