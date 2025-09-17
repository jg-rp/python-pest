import timeit

from pest import DEFAULT_OPTIMIZER
from pest import DUMMY_OPTIMIZER
from pest import Parser

with open("tests/grammars/toml.pest", encoding="utf-8") as fd:
    grammar = fd.read()

with open("tests/examples/example.toml", encoding="ascii") as fd:
    data = fd.read()

optimized_http_parser = Parser.from_grammar(grammar, debug=True)

if DEFAULT_OPTIMIZER.log:
    print(f"{len(DEFAULT_OPTIMIZER.log)} optimized expressions:")
    for entry in DEFAULT_OPTIMIZER.log:
        print(f"  {entry}")
else:
    print("Zero optimizations applied!")


unoptimized_http_parser = Parser.from_grammar(
    grammar, optimizer=DUMMY_OPTIMIZER, debug=True
)


def run_optimized() -> None:
    optimized_http_parser.parse("toml", data)


def run_unoptimized() -> None:
    unoptimized_http_parser.parse("toml", data)


n_runs = 2
n_repeat = 3

t_optimized = min(timeit.repeat(run_optimized, number=n_runs, repeat=n_repeat))
print("\nOptimized:   ", t_optimized)

t_unoptimized = min(timeit.repeat(run_unoptimized, number=n_runs, repeat=n_repeat))
print("Unoptimized: ", t_unoptimized)
