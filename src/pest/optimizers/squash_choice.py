# TODO:
# def collapse_negpred_any(expr: Expression) -> Expression:
#     if (
#         isinstance(expr, Repeat)
#         and isinstance(expr.expression, Sequence)
#     ):
#         seq = expr.expression
#         if (
#             isinstance(seq.left, NegPred)
#             and isinstance(seq.left.expression, Choice)
#             and isinstance(seq.right, Builtin)
#             and seq.right.name == "ANY"
#         ):
#             forbidden = []
#             for alt in seq.left.expression.alternatives:
#                 if isinstance(alt, Literal) and len(alt.value) == 1:
#                     forbidden.append(re.escape(alt.value))
#                 elif isinstance(alt, Builtin) and alt.name == "NEWLINE":
#                     forbidden.append(r"\n")
#                 else:
#                     return expr

#             return Regex(f"[^{''.join(forbidden)}]+")
#     return expr

# TODO:

# def collapse_literal_choice(expr: Expression) -> Expression:
#     if isinstance(expr, Choice):
#         literals = []
#         stack = [expr]
#         while stack:
#             node = stack.pop()
#             if isinstance(node, Choice):
#                 stack.extend([node.left, node.right])
#             elif isinstance(node, Literal) and len(node.value) == 1:
#                 literals.append(re.escape(node.value))
#             else:
#                 return expr  # not all are single-char literals

#         if literals:
#             return Regex(f"[{''.join(literals)}]")
#     return expr


# TODO: usage

# for name, rule in grammar.rules.items():
#     grammar.rules[name].expression = registry.optimize(rule.expression)
