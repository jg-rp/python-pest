from pest import Parser


parser = Parser.from_grammar(
    """\
start      = { SOI ~ ANY ~ EOI }
COMMENT = _{ "#" ~ (!NEWLINE ~ ANY)* }
WHITESPACE = _{ " " | NEWLINE }
""",
)

parse_tree = parser.parse("start", "  x  ")

# print(parser.rules["SKIP"].tree_view())

print(parser.tree_view())
print(parse_tree.dumps(compact=True))

# TODO: optimize sequence of literals ending with skip until
# TODO: optimize sequence of choice of literals followed by skip until
# TODO: remove group if it has a single expression of lazy choice
