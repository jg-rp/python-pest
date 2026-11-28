import timeit

from pest import Parser

with open("tests/grammars/http.pest", encoding="utf-8") as fd:
    grammar = fd.read()

with open("benchmarks/requests.http", encoding="ascii") as fd:
    data = fd.read()


PARSER = Parser.from_grammar(grammar)


n_runs = 20
n_repeat = 3

t_unoptimized = min(
    timeit.repeat(
        'PARSER.parse("http", data)',
        globals={"PARSER": PARSER, "data": data},
        number=n_runs,
        repeat=n_repeat,
    )
)
print("Unoptimized:           ", t_unoptimized)
