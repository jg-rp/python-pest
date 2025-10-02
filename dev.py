import json
import types

from pest import Pairs
from pest import Parser


class GeneratedParser:
    def __init__(self, code: str, *, module_name: str = "generated_parser"):
        # Create an in-memory module for the generated code
        module = types.ModuleType(module_name)
        exec(compile(code, filename=f"{module_name}.py", mode="exec"), module.__dict__)  # noqa: S102
        # Keep a reference to the generated entry point
        self._parse = module.parse

    def parse(self, start_rule: str, input_: str, *, start_pos: int = 0) -> Pairs:
        return self._parse(start_rule, input_, start_pos=start_pos)


with open("tests/grammars/toml.pest", encoding="utf-8") as fd:
    grammar = fd.read()


parser = Parser.from_grammar(grammar)

# print(parser.tree_view())

# with open("tmp.py", "w") as fd:
#     fd.write(parser.generate())

# g_parser = GeneratedParser(parser.generate())


# pairs = g_parser.parse("inline_table", "{ a = 'b' }")
from tmp import parse_inline_table
from pest.grammar.codegen.state import State

pairs = parse_inline_table(State("{ a = 'b' }"))
print(json.dumps(pairs.as_list(), indent=2))

# TODO: Attach rule tags in generated code
