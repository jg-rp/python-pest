import timeit

from pest import Parser

with open("tests/grammars/http.pest", encoding="utf-8") as fd:
    grammar = fd.read()

with open("benchmarks/requests.http", encoding="ascii") as fd:
    data = fd.read()


optimized_http_parser = Parser.from_grammar(grammar)
unoptimized_http_parser = Parser.from_grammar(grammar, optimize=False)


def run_optimized() -> None:
    optimized_http_parser.parse("http", data)


def run_unoptimized() -> None:
    unoptimized_http_parser.parse("http", data)


n_runs = 2
n_repeat = 3

t_optimized = min(timeit.repeat(run_optimized, number=n_runs, repeat=n_repeat))
print("Optimized:   ", t_optimized)

t_unoptimized = min(timeit.repeat(run_unoptimized, number=n_runs, repeat=n_repeat))
print("Unoptimized: ", t_unoptimized)
