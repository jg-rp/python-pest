"""A translation of the CSV example found in the pest book.

https://pest.rs/book/examples/csv.html

This example uses the same grammar and input as examples/csv/, but in a single
file. It shows how you can include a grammar as a raw string instead of
reading it from a file, and without worrying a double escaping special
characters.

Here's a copy of the pest book's license:

https://github.com/pest-parser/book/blob/master/LICENSE-MIT

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from pest import Pair
from pest import Parser

GRAMMAR = r"""
field = { (ASCII_DIGIT | "." | "-")+ }
record = { field ~ ("," ~ field)* }
file = { SOI ~ (record ~ ("\r\n" | "\n"))* ~ EOI }
"""

# NOTE: This simple example grammar requires input CSV to include a trailing
# `\r\n` or `\n`. Without it you will get a `PestParsingError`.

UNPARSED_CSV = """\
65279,1179403647,1463895090
3.1415927,2.7182817,1.618034
-40,-273.15
13,42
65537
"""

parser = Parser.from_grammar(GRAMMAR)


# "file" is the name of the rule to start from.
# Raises a `PestParsingError` if `unparsed_file` fails to parse.
parse_tree = parser.parse("file", UNPARSED_CSV).first()

field_sum = 0.0
record_count = 0

for record in parse_tree:
    match record:
        case Pair("record", fields):  # { field ~ ("," ~ field)* }
            record_count += 1
            for field in fields:
                field_sum += float(field.text)
        case Pair("EOI"):
            break
        case _:
            raise Exception(f"unexpected rule {record.name!r}")


print(f"Sum of fields: {field_sum}")  # noqa: T201
print(f"Number of records: {record_count}")  # noqa: T201
