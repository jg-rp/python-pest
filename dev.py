import json

from pest import Parser

with open("tests/grammars/sql.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)

pairs = parser.parse("Command", "select * from table")

print(json.dumps(pairs.as_list(), indent=2))

# with open("tests/examples/example.http", encoding="ascii") as fd:
#     example = fd.read()

# parser.parse("http", example)


# [
#     Pair {
#         rule: main,
#         span: Span {
#             str: "aabb",
#             start: 0,
#             end: 4,
#         },
#         inner: [
#             Pair {
#                 rule: inner,
#                 span: Span {
#                     str: "aabb",
#                     start: 0,
#                     end: 4,
#                 },
#                 inner: [
#                     Pair {
#                         rule: a,
#                         span: Span {
#                             str: "a",
#                             start: 0,
#                             end: 1,
#                         },
#                         inner: [],
#                     },
#                     Pair {
#                         rule: a,
#                         node_tag: "tag",
#                         span: Span {
#                             str: "a",
#                             start: 1,
#                             end: 2,
#                         },
#                         inner: [],
#                     },
#                 ],
#             },
#             Pair {
#                 rule: EOI,
#                 span: Span {
#                     str: "",
#                     start: 4,
#                     end: 4,
#                 },
#                 inner: [],
#             },
#         ],
#     },
# ]
