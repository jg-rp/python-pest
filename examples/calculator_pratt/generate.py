from pest import Parser

if __name__ == "__main__":
    with open("examples/calculator_pratt/calculator.pest") as fd:
        parser = Parser.from_grammar(fd.read())

    with open("examples/calculator_pratt/parser.py", "w", encoding="utf-8") as fd:
        fd.write(parser.generate())
