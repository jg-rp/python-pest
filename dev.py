from pest.grammar import Parser
from pest.grammar import tokenize

with open("tests/grammars/grammar.pest", encoding="utf-8") as fd:
    source = fd.read()

tokens = tokenize(source)
parser = Parser(tokens)
grammar = parser.parse()

print(grammar)


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
