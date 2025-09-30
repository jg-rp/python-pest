from pest.grammar.codegen.builder import Builder
from pest.grammar.rule import Rule

# TODO: finish me
PRELUDE = """\
from typing import Callable

from pest.grammar.codegen.state import State
from pest.pairs import Pair
"""


def generate_module(rules: dict[str, Rule]) -> str:
    """"""
    # TODO:
    raise NotImplementedError


def generate_rule(rule: Rule) -> str:
    """"""
    inner_gen = Builder()
    rule.generate(inner_gen, "")

    gen = Builder()
    func_name = f"parse_{rule.name}"

    gen.writeln(f"def _{func_name}() -> Callable[[State], Pairs]:")
    with gen.block():
        if inner_gen.rule_constants:
            # Emit rule-scoped constants
            for name, expr in inner_gen.rule_constants:
                gen.writeln(f"{name} = {expr}")
            gen.writeln("")

        gen.writeln(f"rule_frame = RuleFrame({rule.name!r}, {rule.modifier})")

        for line in inner_gen.lines:
            gen.lines.append("    " * gen.indent + line)
        gen.writeln("")
        gen.writeln("return inner")
        gen.writeln("")

    # Instantiate closure.
    gen.writeln(f"{func_name} = _{func_name}()")

    return gen.render()


def generate_parse_trivia(rules: dict[str, Rule]) -> str:
    """Generate a `parse_trivia` function that parses implicit rules.

    If neither `WHITESPACE`, `COMMENT` or the optimized `SKIP` rule exist in
    `rules`, the generated function will be a no-op.
    """
    # TODO
    raise NotImplementedError
