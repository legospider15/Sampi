import re

TOKEN_SPEC = [
    ("NUMBER", r"\d+(?:\.\d+)?"),

    ("STRING", r'"[^"]*"'),
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),

    ("EQUALITY", r"="),
    ("NOT_EQUAL", r"!="),
    ("LESS_EQUAL", r"<="),
    ("GREATER_EQUAL", r">="),
    ("LESS", r"<"),
    ("GREATER", r">"),

    ("LPAR", r"\("),
    ("RPAR", r"\)"),
    ("LBRAK", r"\["),
    ("RBRAK", r"\]"),
    ("LCURL", r"\{"),
    ("RCURL", r"\}"),

    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("POWER", r"\^"),
    ("MOD", r"%"),
    ("NEG", r"~"),

    ("COLON", r":"),
    ("DOT", r"\."),
    ("COMMA", r","),

    ("COMMENT", r"#.*"),

    ("SPACE", r"[ \t]+"),
    ("NEWLINE", r"\n"),
    
    ("UNKNOWN", r".")
]

token_regex = "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPEC)

KEYWORDS = {k: v for k, v in [(i, i.upper()) for i in
[
"set",
"if",
"else",
"end",
"repeat",
"until",
"as",
"in",
"func",
"return",
"or",
"and",
"not",
"to",
"exit",
"use",
"glue",
"find"
]]}

def lex(code):
    tokens = []
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group()

        if kind in ("SPACE", "NEWLINE"):
            continue
        
        elif kind == "STRING":
            tokens.append(("STRING", value.removeprefix('"').removesuffix('"')))

        elif kind == "IDENT" and value in KEYWORDS:
            tokens.append((KEYWORDS[value], value))

        elif kind == "UNKNOWN":
            raise SyntaxError(f"unknown character '{value}'")

        else:
            tokens.append((kind, value))

    tokens.append(("EOF", ""))
    return tokens

def lex_highlight(code):
    tokens = []
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group()

        if kind in ("SPACE", "NEWLINE"):
            continue

        elif kind == "IDENT" and value in KEYWORDS:
            tokens.append((KEYWORDS[value], value))

        else:
            tokens.append((kind, value))

    tokens.append(("EOF", ""))
    return tokens