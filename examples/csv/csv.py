"""A translation of the CSV example found in the pest book.

https://pest.rs/book/examples/csv.html
"""

from pest import Pair
from pest import Parser

with open("examples/csv/csv.pest") as fd:
    grammar = fd.read()

with open("examples/csv/example.csv", encoding="ascii") as fd:
    unparsed_file = fd.read()

parser = Parser.from_grammar(grammar)


# "file" is the name of the rule to start from.
# Raises a `PestParsingError` if `unparsed_file` fails to parse.
file = parser.parse("file", unparsed_file).first()

field_sum = 0.0
record_count = 0

for record in file:
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
