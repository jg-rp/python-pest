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
    """Generate the full parser function for a single rule.

    Returns the source of a top-level assignment:
        parse_<rule> = _parse_<rule>()

    Where `_parse_<rule>` defines a closure with:
      - a `rule_frame` (RuleFrame with name + modifier),
      - any rule-local constants,
      - and the `inner(state, pairs)` function that implements the body.
    """
    # First, generate the inner function body
    inner_gen = Builder()
    rule.generate(inner_gen, "")

    # Now build the outer closure
    gen = Builder()
    func_name = f"parse_{rule.name}"

    gen.writeln(f"def _{func_name}() -> Callable[[State, list[Pair]], None]:")
    with gen.block():
        # Emit rule-scoped constants (regexes, tables, etc.)
        if inner_gen.rule_constants:
            for name, expr in inner_gen.rule_constants:
                gen.writeln(f"{name} = {expr}")
            gen.writeln("")  # spacer after constants

        # Each closure has its own RuleFrame
        gen.writeln(f"rule_frame = RuleFrame({rule.name!r}, {rule.modifier})")
        gen.writeln("")

        # Inline the inner function body generated earlier
        for line in inner_gen.lines:
            gen.writeln(line)
        gen.writeln("")

        # Expose the inner parser function
        gen.writeln("return inner")
        gen.writeln("")

    # At module scope, instantiate the closure
    gen.writeln(f"{func_name} = _{func_name}()")

    return gen.render()


def generate_parse_trivia(rules: dict[str, Rule]) -> str:
    """Generate a `parse_trivia` function that parses implicit rules.

    If neither `WHITESPACE`, `COMMENT` nor the optimized `SKIP` rule exist in
    `rules`, the generated function will be a no-op.
    """
    has_skip = "SKIP" in rules
    has_ws = "WHITESPACE" in rules
    has_comment = "COMMENT" in rules

    gen = Builder()
    gen.writeln("def parse_trivia(state: ParserState, pairs: list[Pair]) -> None:")
    with gen.block():
        if not (has_skip or has_ws or has_comment):
            # Nothing to do
            gen.writeln("pass")
            return gen.render()

        if has_skip:
            gen.writeln("if state.atomic_depth > 0:")
            with gen.block():
                gen.writeln("return")
            gen.writeln("parse_SKIP(state, pairs)")
            return gen.render()

        gen.writeln("children: list[Pair] = []")
        gen.writeln("while True:")
        with gen.block():
            gen.writeln("state.checkpoint()")
            gen.writeln("matched = False")

            if has_ws:
                gen.writeln("try:")
                with gen.block():
                    gen.writeln("parse_WHITESPACE(state, children)")
                    gen.writeln("pairs.extend(children)")
                    gen.writeln("state.ok()")
                    gen.writeln("matched = True")
                    gen.writeln("children.clear()")
                    gen.writeln("continue")
                gen.writeln("except ParseError:")
                with gen.block():
                    gen.writeln("state.restore()")

            if has_comment:
                gen.writeln(
                    "if not state.rule_stack or state.rule_stack[-1].name != 'COMMENT':"
                )
                with gen.block():
                    gen.writeln("try:")
                    with gen.block():
                        gen.writeln("parse_COMMENT(state, children)")
                        gen.writeln("pairs.extend(children)")
                        gen.writeln("state.ok()")
                        gen.writeln("matched = True")
                        gen.writeln("children.clear()")
                    gen.writeln("except ParseError:")
                    with gen.block():
                        gen.writeln("state.restore()")

            gen.writeln("if not matched:")
            with gen.block():
                gen.writeln("break")

    return gen.render()
