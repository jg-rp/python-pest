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


with open("tests/grammars/toml.pest", encoding="utf-8") as fd:
    grammar = fd.read()

with open("tests/examples/example.toml", encoding="utf-8") as fd:
    data = fd.read()

unoptimized_toml_parser = Parser.from_grammar(grammar, optimizer=None, debug=True)
# print(unoptimized_toml_parser.tree_view())

optimized_toml_parser = Parser.from_grammar(grammar, debug=True)

if DEFAULT_OPTIMIZER.log:
    print(f"{len(DEFAULT_OPTIMIZER.log)} optimized expressions:")
    for entry in DEFAULT_OPTIMIZER.log:
        print(f"  {entry}")
    # print("")
    # print(optimized_toml_parser.tree_view())
else:
    print("Zero optimizations applied!")

generated_toml_parser = GeneratedParser(unoptimized_toml_parser.generate())
optimized_generated_toml_parser = GeneratedParser(optimized_toml_parser.generate())


def run_optimized() -> None:
    optimized_toml_parser.parse("toml", data)


def run_unoptimized() -> None:
    unoptimized_toml_parser.parse("toml", data)


def run_generated_unoptimized() -> None:
    generated_toml_parser.parse("toml", data)


def run_generated_optimized() -> None:
    optimized_generated_toml_parser.parse("toml", data)


n_runs = 100
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
