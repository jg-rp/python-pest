"""Aho-Corasick-based `index_any`."""

from collections import deque
from collections.abc import Sequence


class _AhoCorasick:
    def __init__(self, patterns: Sequence[str]) -> None:
        self.trie: dict[int, dict[str, int]] = {}
        self.fail: dict[int, int] = {}
        self.output: dict[int, list[str]] = {}
        self._build_trie(patterns)
        self._build_failures()

    def _build_trie(self, patterns: Sequence[str]) -> None:
        """Build the trie structure from patterns."""
        self.trie = {0: {}}  # root node
        new_state = 1

        for pat in patterns:
            state = 0
            for ch in pat:
                if ch not in self.trie[state]:
                    self.trie[state][ch] = new_state
                    self.trie[new_state] = {}
                    new_state += 1
                state = self.trie[state][ch]
            self.output.setdefault(state, []).append(pat)

    def _build_failures(self) -> None:
        """Add failure links for the AC automaton."""
        self.fail = {}
        queue: deque[int] = deque()

        # Level 1 nodes fail to root
        for _, nxt in self.trie[0].items():
            self.fail[nxt] = 0
            queue.append(nxt)

        while queue:
            state = queue.popleft()
            for ch, nxt in self.trie[state].items():
                queue.append(nxt)

                # follow failure links
                f = self.fail[state]
                while f and ch not in self.trie[f]:
                    f = self.fail[f]
                self.fail[nxt] = self.trie[f].get(ch, 0)

                # merge outputs
                if self.fail[nxt] in self.output:
                    self.output.setdefault(nxt, []).extend(self.output[self.fail[nxt]])

    def find_first(self, s: str, start: int = 0) -> tuple[int, str] | None:
        """Return (index, pattern) of the earliest match at or after `start`.

        Return None if no match exists.
        """
        state = 0
        best: tuple[int, str] | None = None

        for i in range(start, len(s)):
            ch = s[i]
            while state and ch not in self.trie[state]:
                state = self.fail[state]
            state = self.trie[state].get(ch, 0)

            if state in self.output:
                for pat in self.output[state]:
                    pos = i - len(pat) + 1
                    if best is None or pos < best[0]:
                        best = (pos, pat)

                # since we scan left-to-right, we can stop early
                # as soon as we confirm a match at position `i - len(pat) + 1`
                # and it's the leftmost possible.
                if best and best[0] == i - len(best[1]) + 1:
                    return best

        return best


def index_any(s: str, subs: Sequence[str], start: int = 0) -> int:
    """Like str.index, but accepts a sequence of substrings.

    Uses Aho-Corasick for efficient multi-pattern search.
    """
    ac = _AhoCorasick(subs)
    match = ac.find_first(s, start)
    if match is None:
        raise ValueError("substrings not found")
    return match[0]
