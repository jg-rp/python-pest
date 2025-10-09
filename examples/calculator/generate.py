from pest import Parser

if __name__ == "__main__":
    with open("examples/calculator/calculator.pest") as fd:
        parser = Parser.from_grammar(fd.read())

    with open("examples/calculator/parser.py", "w", encoding="utf-8") as fd:
        fd.write(parser.generate())

    with open("examples/calculator/implicit_prec.pest") as fd:
        parser = Parser.from_grammar(fd.read())

    with open(
        "examples/calculator/implicit_prec_parser.py", "w", encoding="utf-8"
    ) as fd:
        fd.write(parser.generate())
