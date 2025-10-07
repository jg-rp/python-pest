"""Example calculator precedence climbing parser.

If running this from the root of the Python pest repo, use
`python -m examples.calculator`
"""

import json

from pest import Pairs

from .parser import Rule
from .parser import parse


def main() -> None:
    # TODO: get expression from stdin
    pairs = parse(Rule.PROGRAM, "1 + 2")
    print(json.dumps(pairs.as_list(), indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
