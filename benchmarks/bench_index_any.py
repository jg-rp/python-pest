import random
import string
import timeit
from collections.abc import Sequence
from typing import Optional

from pest.grammar.ac_index_any import _AhoCorasick


def index_any_simple(s: str, subs: Sequence[str], start: int = 0) -> int:
    best_index: Optional[int] = None
    for sub in subs:
        pos = s.find(sub, start)
        if pos != -1 and (best_index is None or pos < best_index):
            best_index = pos
    if best_index is None:
        return -1
    return best_index


def make_random_text(length: int = 20000) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))  # noqa: S311


def make_random_substrings(n: int, length: int = 15) -> list[str]:
    return ["".join(random.choices(string.ascii_lowercase, k=length)) for _ in range(n)]  # noqa: S311


def benchmark(n_subs: int, n_runs: int = 10, n_repeat: int = 5) -> tuple[float, float]:
    text = make_random_text()
    subs = make_random_substrings(n_subs, 5)
    ac = _AhoCorasick(subs)

    def run_simple() -> int:
        return index_any_simple(text, subs)

    def run_ac() -> object:
        return ac.find_first(text)

    t_simple = min(timeit.repeat(run_simple, number=n_runs, repeat=n_repeat))
    t_ac = min(timeit.repeat(run_ac, number=n_runs, repeat=n_repeat))

    return t_simple / n_runs, t_ac / n_runs


if __name__ == "__main__":
    print(f"{'subs':>6} | {'simple (ms)':>12} | {'AC search (ms)':>15}")
    print("-" * 40)
    for n in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]:
        t_simple, t_ac = benchmark(n, n_runs=5)
        print(f"{n:6d} | {t_simple * 1000:12.3f} | {t_ac * 1000:15.3f}")
