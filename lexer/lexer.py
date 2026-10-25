import re

TOKEN_SPECIFICATION = [
    ("NUMBER", r"\d+(?:.\d+)?"),
    ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("RELATIONAL_OPERATOR", r"==|!=|>=|<=|>|<"),
    ("LOGICAL_OPERATOR", r"&&|\|\||!"),
    ("LPAREN", r"("),
    ("RPAREN", r")"),
    ("WHITESPACE", r"\s+"),
]

MASTER_PATTERN = re.compile(
    "|".join(
        f"(?P<{name}>{pattern})"
        for name, pattern in TOKEN_SPECIFICATION
    )
)


class LexicalError(Exception):
    pass


def tokenize(expression):
    tokens = []
    position = 0

    while position < len(expression):
        match = MASTER_PATTERN.match(expression, position)

        if not match:
            character = expression[position]
            raise LexicalError(
                f"Unexpected character '{character}' "
                f"at position {position}"
            )

        token_type = match.lastgroup
        lexeme = match.group()

        if token_type != "WHITESPACE":
            tokens.append({
                "lexeme": lexeme,
                "type": token_type,
                "position": position
            })

        position = match.end()

    return tokens


if name == "main":
    expression = input("Enter a Boolean expression: ")

    try:
        result = tokenize(expression)

        print("\nTOKEN ANALYSIS")
        print("-" * 50)

        for token in result:
            print(
                f"Lexeme: {token['lexeme']:<10} "
                f"Type: {token['type']}"
            )

        print("\nLexical analysis completed successfully.")

    except LexicalError as error:
        print("\nLEXICAL ERROR:", error)
