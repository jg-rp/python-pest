from pest import Parser
from pest.grammar.codegen.builder import Builder
from pest.grammar.codegen.generate import generate_parse_trivia
from pest.grammar.codegen.generate import generate_rule
from pest.grammar.rule import Rule

# with open("tests/grammars/toml.pest", encoding="utf-8") as fd:
#     grammar = fd.read()

grammar = """\
WHITESPACE = _{ " " | "\t" | NEWLINE }
COMMENT    = _{ "#" ~ (!NEWLINE ~ ANY)* }
"""

rules = Parser.from_grammar(grammar).rules
# rules = Parser.from_grammar(grammar).rules

# TODO: Attach rule tags in generated code
# TODO: generate_module
#    - Prelude
#       - imports
#           - Callable
#           - ParseError
#           - State
#           - Pair
#       - RuleFrame
#       - modifier bit masks


print(generate_parse_trivia(rules))
