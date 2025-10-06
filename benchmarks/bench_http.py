import timeit
import types

from pest import DEFAULT_OPTIMIZER
from pest import Pairs
from pest import Parser


class GeneratedParser:
    def __init__(self, code: str, *, module_name: str = "generated_parser"):
        # Create an in-memory module for the generated code
        module = types.ModuleType(module_name)
        exec(compile(code, filename=f"{module_name}.py", mode="exec"), module.__dict__)  # noqa: S102
        # Keep a reference to the generated entry point
        self._parse = module.parse

    def parse(self, start_rule: str, input_: str, *, start_pos: int = 0) -> Pairs:  # noqa: D102
        return self._parse(start_rule, input_, start_pos=start_pos)


with open("tests/grammars/http.pest", encoding="utf-8") as fd:
    grammar = fd.read()

with open("benchmarks/requests.http", encoding="ascii") as fd:
    data = fd.read()

unoptimized_http_parser = Parser.from_grammar(grammar, optimizer=None, debug=True)
# print(unoptimized_http_parser.tree_view())

optimized_http_parser = Parser.from_grammar(grammar, debug=True)

if DEFAULT_OPTIMIZER.log:
    print(f"{len(DEFAULT_OPTIMIZER.log)} optimized expressions:")
    for entry in DEFAULT_OPTIMIZER.log:
        print(f"  {entry}")
    # print("\n", optimized_http_parser.tree_view())
else:
    print("Zero optimizations applied!")


generated_http_parser = GeneratedParser(unoptimized_http_parser.generate())
optimized_generated_http_parser = GeneratedParser(optimized_http_parser.generate())


def run_optimized() -> None:
    optimized_http_parser.parse("http", data)


def run_unoptimized() -> None:
    unoptimized_http_parser.parse("http", data)


def run_generated_unoptimized() -> None:
    generated_http_parser.parse("http", data)


def run_generated_optimized() -> None:
    optimized_generated_http_parser.parse("http", data)


n_runs = 20
n_repeat = 3

t_optimized = min(timeit.repeat(run_optimized, number=n_runs, repeat=n_repeat))
print("\nOptimized:             ", t_optimized)

t_unoptimized = min(timeit.repeat(run_unoptimized, number=n_runs, repeat=n_repeat))
print("Unoptimized:           ", t_unoptimized)

t_generated_optimized = min(
    timeit.repeat(run_generated_optimized, number=n_runs, repeat=n_repeat)
)
print("Generated optimized:   ", t_generated_optimized)

t_generated_unoptimized = min(
    timeit.repeat(run_generated_unoptimized, number=n_runs, repeat=n_repeat)
)
print("Generated unoptimized: ", t_generated_unoptimized)
