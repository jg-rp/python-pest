"""Exceptions that occur when parsing an input with a pest grammar."""

from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pest.state import ParserState


class PestParsingError(Exception):
    """An exception raised when an input string can't be passed by a pest grammar."""

    # TODO: docs

    def __init__(self, state: ParserState):
        super().__init__(
            self.expected(state.furthest_expected, state.furthest_unexpected)
        )
        self.state = state

    def __str__(self) -> str:
        return self.detailed_message()

    def detailed_message(self) -> str:
        """Return an error message formatted with extra context info."""
        line, lineno, col = error_context(self.state.input, self.state.furthest_pos)

        msg = self.args[0]
        pad = " " * len(str(lineno))
        pointer = (" " * (col - 1)) + "^"
        no_pointer = " " * (col)
        rule_stack = " > ".join(f.name for f in self.state.furthest_stack)

        # TODO: if this is short, put it on the same line as msg
        # TODO: suppress this if `(None)`
        labels = self.expected_labels(
            self.state.furthest_expected, self.state.furthest_unexpected
        )

        return (
            f"{msg}\n"
            f"{pad} -> {rule_stack} {lineno}:{col}\n"
            f"{pad} |\n"
            f"{lineno} | {line}\n"
            f"{pad} | {pointer} {msg}\n"
            f"{pad} | {no_pointer} ({labels})\n"
        )

    def expected(
        self, expected: dict[str, list[str]], unexpected: dict[str, list[str]]
    ) -> str:
        """Return the expected/unexpected part of a detailed error message."""
        if expected and not unexpected:
            return "expected " + join_with_limit(
                list(expected), ", ", last_separator=" or "
            )

        if expected and unexpected:
            _expected = "expected " + join_with_limit(
                list(expected), ", ", last_separator=" or ", limit=40
            )

            _unexpected = "unexpected " + join_with_limit(
                list(unexpected), ", ", last_separator=" or ", limit=40
            )

            return f"{_unexpected}; {_expected}"

        if unexpected:
            return "unexpected " + join_with_limit(
                list(unexpected), ", ", last_separator=" or "
            )

        # Not context available
        return "pest parsing error"

    def expected_labels(
        self, expected: dict[str, list[str]], unexpected: dict[str, list[str]]
    ) -> str | None:
        """Return a string representation of expected and unexpected labels."""
        if expected and not unexpected:
            return join_with_limit(
                list(chain(*expected.values())), ", ", last_separator=" or "
            )

        if expected and unexpected:
            _expected = join_with_limit(
                list(chain(*expected.values())), ", ", last_separator=" or ", limit=40
            )

            _unexpected = "not " + join_with_limit(
                list(chain(*unexpected.values())), ", ", last_separator=" or ", limit=40
            )

            return f"{_unexpected}; {_expected}"

        if unexpected:
            return "not " + join_with_limit(
                list(chain(*unexpected.values())), ", ", last_separator=" or "
            )

        return None


def join_with_limit(  # noqa: PLR0911
    items: list[str],
    separator: str = ", ",
    last_separator: str | None = None,
    limit: int = 80,
) -> str:
    """Join a list of strings with a character-length limit.

    The function joins items using `separator` between most items, and optionally
    uses `last_separator` before the final item (e.g., ", " and " or " to produce
    "a, b or c"). The total output length, including separators and any suffix,
    will never exceed `limit`.

    Truncation behavior:
        • If all items fit, returns the full joined string.
        • If truncation is needed, includes as many items as possible and appends
          "…(+N more)".
        • When truncating, only the normal separator is used before the ellipsis;
          the `last_separator` is reserved for full output.
        • If even the first item doesn’t fit, returns "(N items)" if possible.
        • Returns "" if nothing fits.

    Args:
        items (list[str]): The list of strings to join.
        separator (str): The separator used between most items (default: ", ").
        last_separator (str | None): The separator used before the last item
            (e.g., " or "). If None, uses `separator` for all.
        limit (int): Maximum total output length (default: 80).

    Returns:
        str: Joined string representation, truncated or summarized if necessary.
    """
    if not items or limit <= 0:
        return ""

    # Handle single item
    if len(items) == 1:
        if len(items[0]) <= limit:
            return items[0]
        summary = "(1 items)"
        return summary if len(summary) <= limit else ""

    # Helper for full join
    def join_all(lst: list[str]) -> str:
        if last_separator and len(lst) > 1:
            return separator.join(lst[:-1]) + last_separator + lst[-1]
        return separator.join(lst)

    # Try full join first
    joined = join_all(items)
    if len(joined) <= limit:
        return joined

    # Incremental truncation loop
    result_parts: list[str] = []
    current_length = 0

    for idx, item in enumerate(items):
        sep_len = len(separator) if result_parts else 0
        added_length = sep_len + len(item)
        remaining_count = len(items) - (idx + 1)
        suffix = f"…(+{remaining_count} more)" if remaining_count > 0 else ""
        total_length = current_length + added_length + len(suffix)

        if total_length > limit:
            break

        if result_parts:
            current_length += len(separator)
        result_parts.append(item)
        current_length += len(item)

    if result_parts:
        # Truncation occurred
        if len(result_parts) < len(items):
            remaining_count = len(items) - len(result_parts)
            suffix = f"…(+{remaining_count} more)"
            candidate = separator.join(result_parts) + suffix
            if len(candidate) <= limit:
                return candidate

        # All items fit within limit (no truncation needed)
        if last_separator and len(result_parts) > 1:
            return separator.join(result_parts[:-1]) + last_separator + result_parts[-1]
        return separator.join(result_parts)

    # Fallback summary if nothing fits
    summary = f"({len(items)} items)"
    return summary if len(summary) <= limit else ""


def error_context(text: str, index: int) -> tuple[str, int, int]:
    """Return a (line, lineno, col) tuple for position `index` in `text`."""
    if not text:
        return ("", 1, 0)

    lines = text.splitlines(keepends=True)
    cumulative_length = 0
    target_line_index = len(lines) - 1

    for i, line in enumerate(lines):
        cumulative_length += len(line)
        if index < cumulative_length:
            target_line_index = i
            break

    # Line number (1-based)
    line_number = target_line_index + 1
    # Column number within the line
    column_number = index - (cumulative_length - len(lines[target_line_index])) + 1
    current_line = lines[target_line_index].rstrip()

    return (current_line, line_number, column_number)
