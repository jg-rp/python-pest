"""Exceptions that occur when parsing an input with a pest grammar."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pest.grammar import Rule


class PestParsingError(Exception):
    """An exception raised when an input string can't be passed by a pest grammar."""

    def __init__(
        self,
        rule_stack: list[Rule],
        positives: list[str],
        negatives: list[str],
        pos: int,
        line: str,
        lineno: int,
        col: int,
    ):
        super().__init__(f"expected {join_with_limit(positives, ' or ')}")
        self.rule_stack = rule_stack
        self.positives = positives
        self.negatives = negatives
        self.pos = pos
        self.line = line
        self.lineno = lineno
        self.col = col

    def __str__(self) -> str:
        return self.detailed_message()

    def detailed_message(self) -> str:
        """Return an error message formatted with extra context info."""
        # TODO: use rule_stack
        msg = self.args[0]
        pad = " " * len(str(self.lineno))
        pointer = (" " * self.col) + "^"

        return (
            f"{' > '.join(f.name for f in self.rule_stack)}\n"
            f"{pad} -> {self.lineno}:{self.col}\n"
            f"{pad} |\n"
            f"{self.lineno} | {self.line}\n"
            f"{pad} | {pointer} {msg}\n"
        )


def join_with_limit(items: list[str], separator: str = ", ", limit: int = 80) -> str:  # noqa: PLR0911
    """Join a list of strings into a single string with a character-length limit.

    The function joins items from the list using the provided separator, ensuring
    that the total length of the resulting string (including any truncation suffix)
    does not exceed the given character `limit`. Items are always included in full:
    truncation occurs only at item boundaries, never in the middle of a word or
    separator.

    Truncation behavior:
        • If all items fit within the limit, the function returns the full joined
          string.
        • If not all items fit, it joins as many items as possible and appends an
          ellipsis-based suffix of the form:
              "…(+N more)"
          where `N` is the number of items omitted.
        • If the first item cannot fit (even with truncation), the function falls back
          to returning a summary of the form:
              "(N items)"
          where `N` is the total number of items in the list.
        • If neither the summary nor any item fits within the limit, the function
          returns an empty string.

    This ensures the returned string is concise, readable, and always respects the
    limit.

    Args:
        items (list[str]): The list of strings to join.
        separator (str, optional): The string used to separate items. Defaults to ", ".
        limit (int, optional): The maximum allowed length of the result string,
            including separators and suffixes. Defaults to 80.

    Returns:
        str: A string representation of the list that:
            - Includes as many full items as possible.
            - Appends an ellipsis and item count when truncated ("…(+N more)").
            - Returns "(N items)" when no items can fit.
            - Never exceeds the specified `limit`.
            - Returns an empty string if nothing fits.

    Examples:
        >>> join_with_limit(["apple", "banana", "cherry"], limit=50)
        'apple, banana, cherry'

        >>> join_with_limit(["apple", "banana", "cherry", "date"], ", ", limit=25)
        'apple, banana…(+2 more)'

        >>> join_with_limit(["superlongword"] * 5, limit=10)
        '(5 items)'

        >>> join_with_limit(["superlongword"] * 5, limit=3)
        ''

        >>> join_with_limit([], limit=10)
        ''
    """
    if not items or limit <= 0:
        return ""

    # Handle single-item case explicitly
    if len(items) == 1:
        if len(items[0]) <= limit:
            return items[0]
        summary = "(1 items)"
        if len(summary) <= limit:
            return summary
        return ""

    # Try to fit all items first
    joined = separator.join(items)
    if len(joined) <= limit:
        return joined

    # Try to fit as many items as possible, then add suffix
    result_parts = []
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
        # If not all items fit, add suffix
        if len(result_parts) < len(items):
            remaining_count = len(items) - len(result_parts)
            suffix = f"…(+{remaining_count} more)"
            candidate = separator.join(result_parts) + suffix
            if len(candidate) <= limit:
                return candidate
        # If all items fit, just return joined items
        return separator.join(result_parts)

    # If no items fit, always try summary
    summary = f"({len(items)} items)"
    if len(summary) <= limit:
        return summary
    return ""


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
    column_number = index - (cumulative_length - len(lines[target_line_index]))
    current_line = lines[target_line_index].rstrip()

    return (current_line, line_number, column_number)
