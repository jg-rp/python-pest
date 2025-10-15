"""Pest grammar errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tokens import Token


class PestGrammarError(Exception):
    """Base class for exceptions raised when parsing pest grammars."""

    def __init__(self, *args: object, token: Token | None = None) -> None:
        super().__init__(*args)
        self.token = token

    def __str__(self) -> str:
        return self.detailed_message()

    def detailed_message(self) -> str:
        """Return an error message formatted with extra context info."""
        if not self.token:
            return super().__str__()

        lineno, col, _prev, current, _next = self._error_context(
            self.token.grammar, self.token.start
        )

        # if self.token.kind == TOKEN_EOF:
        #     col = len(current)

        pad = " " * len(str(lineno))
        length = len(self.token.value)
        pointer = (" " * col) + ("^" * max(length, 1))

        return (
            f"{self.message}\n"
            f"{pad} -> {lineno}:{col}\n"
            f"{pad} |\n"
            f"{lineno} | {current}\n"
            f"{pad} | {pointer} {self.message}\n"
        )

    @property
    def message(self) -> object:
        """The exception's error message if one was given."""
        if self.args:
            return self.args[0]
        return None

    def _error_context(self, text: str, index: int) -> tuple[int, int, str, str, str]:
        lines = text.splitlines(keepends=True)
        cumulative_length = 0
        target_line_index = -1

        for i, line in enumerate(lines):
            cumulative_length += len(line)
            if index < cumulative_length:
                target_line_index = i
                break

        if target_line_index == -1:
            raise ValueError("index is out of bounds for the given string")

        # Line number (1-based)
        line_number = target_line_index + 1
        # Column number within the line
        column_number = index - (cumulative_length - len(lines[target_line_index]))

        previous_line = (
            lines[target_line_index - 1].rstrip() if target_line_index > 0 else ""
        )
        current_line = lines[target_line_index].rstrip()
        next_line = (
            lines[target_line_index + 1].rstrip()
            if target_line_index < len(lines) - 1
            else ""
        )

        return line_number, column_number, previous_line, current_line, next_line


class PestGrammarSyntaxError(PestGrammarError):
    """An exception raised due to invalid pest grammar syntax."""
