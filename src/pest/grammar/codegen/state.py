class ParserState:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.user_stack: list[str] = []  # PUSH/POP/PEEK/DROP
        self.modifier_stack: list[int] = []  # bit fields

    def checkpoint(self) -> tuple[int, int, int]:
        """Save restore point: position, user stack size, modifier stack size."""
        return self.pos, len(self.user_stack), len(self.modifier_stack)

    def restore(self, checkpoint: tuple[int, int, int]) -> None:
        pos, stack_len, mod_len = checkpoint
        self.pos = pos
        del self.user_stack[stack_len:]
        del self.modifier_stack[mod_len:]
