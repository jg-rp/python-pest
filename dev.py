import json

from pest import Parser

with open("tests/grammars/sql.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)

# for token in tokenize("repeat_max = { string{, 2} }"):
#     print(token)

pairs = parser.parse(
    "Command",
    '''insert into "my_table" ("col_1", "col_2")
                  select "name", "class", avg("age")
                  from "students"
                  where "age" > 15
                  group by "age"''',
)

# print(parser)

# with open("tests/examples/example.toml", encoding="utf-8") as fd:
#     example = fd.read()

# pairs = parser.parse("toml", example)

print(json.dumps(pairs.as_list(), indent=2))
