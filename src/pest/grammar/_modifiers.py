from ._tokens import TOKEN_AT, TOKEN_DOLLAR, TOKEN_EXCLAIM, TOKEN_UNDERSCORE, TokenKind

SILENT = 1 << 1  # _
ATOMIC = 1 << 2  # @
COMPOUND = 1 << 3  # $
NONATOMIC = 1 << 4  # !

SILENT_ATOMIC = SILENT | ATOMIC
SILENT_COMPOUND = SILENT | COMPOUND
SILENT_NONATOMIC = SILENT | NONATOMIC

MODIFIER_SYMBOLS: dict[int, str] = {
    SILENT: "_",
    ATOMIC: "@",
    COMPOUND: "$",
    NONATOMIC: "!",
}

MODIFIER_MAP: dict[TokenKind, int] = {
    TOKEN_AT: ATOMIC,
    TOKEN_DOLLAR: COMPOUND,
    TOKEN_EXCLAIM: NONATOMIC,
    TOKEN_UNDERSCORE: SILENT,
}


def modifier_to_str(flags: int) -> str:
    """Convert a modifier bit field into a string of symbols, in defined order."""
    return "".join(symbol for bit, symbol in MODIFIER_SYMBOLS.items() if flags & bit)
