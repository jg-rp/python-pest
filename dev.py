from pest import Parser
from pest.grammar.codegen.builder import Builder
from pest.grammar.expression import Expression
from pest.grammar.rule import Rule

# TODO: LazyChoiceRegex.generate
rules = Parser.from_grammar('thing = { "a" | "b" }').rules

# def parse_<rule>(state: ParserState) -> Pairs:


def generate_rule(rule: Rule) -> str:
    gen = Builder()
    rule.generate(gen, "")
    return gen.render()


print(generate_rule(rules["thing"]))
