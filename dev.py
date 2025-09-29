from pest import Parser
from pest.grammar.codegen.builder import Builder
from pest.grammar.rule import Rule

rules = Parser.from_grammar('thing = { ("a" | "b")? ~ !"c" ~ "d" }').rules

# TODO: check implementation of NegativePredicate.generate
# TODO: emit comment to delimit generated code
# TODO: generate for terminals and stack ops


def generate_rule(rule: Rule) -> str:
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

        for line in inner_gen.lines:
            gen.lines.append("    " * gen.indent + line)
        gen.writeln("")
        gen.writeln("return inner")
        gen.writeln("")

    # Instantiate closure.
    gen.writeln(f"{func_name} = _{func_name}()")

    return gen.render()


print(generate_rule(rules["thing"]))
