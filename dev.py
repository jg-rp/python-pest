from pest import Parser

grammar = """\
WHITESPACE  = _{ " " | "\t" | NEWLINE }

program     =  { SOI ~ expr ~ EOI }
expr        =  { add_sub }   // top-level expression

add_sub     =  { mul_div ~ (add_op ~ mul_div)* }
add_op      = _{ add | sub }
  add       =  { "+" }
  sub       =  { "-" }

mul_div     =  { pow_expr ~ (mul_op ~ pow_expr)* }
mul_op      = _{ mul | div }
  mul       =  { "*" }
  div       =  { "/" }

pow_expr    =  { prefix ~ (pow_op ~ pow_expr)? } // right-associative
pow_op      = _{ pow }
  pow       =  { "^" }

prefix      =  { (neg)* ~ postfix }
  neg       =  { "-" }

postfix     =  { primary ~ (fac)* }
  fac       =  { "!" }

primary     = _{ int | ident | "(" ~ expr ~ ")" }
  int       = @{ (ASCII_NONZERO_DIGIT ~ ASCII_DIGIT* | "0") }
  ident     = @{ ASCII_ALPHA+ }
"""

parser = Parser.from_grammar(grammar)
parse_tree = parser.parse("program", "2 * 3 + 4")

print(parse_tree.dumps())
