# grammar = """\
# array      = { "[" ~ int_list ~ "]" }
# int_list   = { int ~ ("," ~ int)* }
# int        = @{ "0" | ASCII_NONZERO_DIGIT  ~ ASCII_DIGIT* }
# WHITESPACE = _{ " " }
# """

# parser = Parser.from_grammar(grammar)
# parse_tree = parser.parse("array", "[1, 2, 3, 42]")

# print(parse_tree.dumps())
# # - array > int_list
# #   - int: "1"
# #   - int: "2"
# #   - int: "3"
# #   - int: "42"

# match parse_tree.first():
#     case Pair("array", [int_list]):
#         numbers = [int(p.text) for p in int_list.inner() if p.name == "int"]
#     case _:
#         raise ValueError("unexpected parse tree")

# print(numbers)


# with open("parser.py", "w", encoding="utf-8") as fd:
#     fd.write(parser.generate())

from parser import Rule
from parser import parse
from pest import Pair

parse_tree = parse(Rule.ARRAY, "[1, 2, 3, 42]")

match parse_tree.first():
    case Pair(Rule.ARRAY, [Pair(Rule.INT_LIST, inner)]):
        numbers = [int(p.text) for p in inner]
    case _:
        raise ValueError("unexpected parse tree")

print(numbers)
