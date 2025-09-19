"""Exceptions that occur when parsing an input with a pest grammar."""


class PestParsingError(Exception):
    """An exception raised when an input string can't be passed by a given rule."""

    def __init__(
        self,
        msg: str,
        positives: list[str],
        negatives: list[str],
        pos: int,
        line: str,
        start: tuple[int, int],
    ):
        super().__init__(msg)
        self.positives = positives
        self.negatives = negatives
        self.pos = pos
        self.line = line
        self.start = start
