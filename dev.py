from pest import Parser


with open("tests/grammars/http.pest", encoding="utf-8") as fd:
    grammar = fd.read()

parser = Parser.from_grammar(grammar)

pairs = parser.parse("version", "1.1")

for token in pairs.tokens():
    print(token)


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
