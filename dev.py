from pest import Parser
from pest.grammar.codegen.builder import Builder
from pest.grammar.expression import Expression
from pest.grammar.rule import Rule

rules = Parser.from_grammar('thing = { "a" | "b" }').rules


def generate_rule(rule: Rule) -> str:
    inner_gen = Builder()
    rule.generate(inner_gen, "")

    gen = Builder()
    func_name = f"parse_{rule.name}"

    gen.writeln(f"def _{func_name}() -> Callable[[State], Pairs]:")
    with gen.block():
        # Emit per-rule constants
        for line in inner_gen.render_constants():
            gen.writeln(line)
        if inner_gen.rule_constants:
            gen.writeln("")

        for line in inner_gen.lines:
            gen.lines.append("    " * gen.indent + line)
        gen.writeln("")

    # Instantiate closure.
    gen.writeln(f"{func_name} = _{func_name}()")

    return gen.render()


print(generate_rule(rules["thing"]))
