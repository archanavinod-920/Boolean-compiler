
class Parser:
    """Recursive-descent parser for Boolean expressions."""

    def __init__(self, tokens):
        # Tokens are dictionaries from the lexer.
        self.tokens = tokens
        self.pos = 0

    def current(self):
        """Return the current token or a synthetic EOF token."""
        if self.pos >= len(self.tokens):
            return {
                "type": "EOF",
                "lexeme": "",
                "position": -1,
            }

        return self.tokens[self.pos]

    def accept(self, token_type, lexeme=None):
        """Consume a token if its type and optional lexeme match."""
        token = self.current()

        if token["type"] != token_type:
            return None

        if lexeme is not None and token["lexeme"] != lexeme:
            return None

        self.pos += 1
        return token

    def expect(self, token_type, lexeme=None):
        """Require a token or raise a syntax error."""
        token = self.accept(token_type, lexeme)

        if token is None:
            found = self.current()["lexeme"] or "end of input"
            expected = lexeme if lexeme is not None else token_type

            raise SyntaxError(
                f"Expected {expected}, found {found}"
            )

        return token

    def parse(self):
        """Parse the complete expression."""
        if not self.tokens:
            raise SyntaxError("Expression cannot be empty")

        node = self.parse_or()

        if self.current()["type"] != "EOF":
            token = self.current()
            raise SyntaxError(
                f"Unexpected token '{token['lexeme']}' "
                f"at position {token.get('position', '?')}"
            )

        return node

    def parse_or(self):
        """OrExpr -> AndExpr (OR AndExpr)*"""
        node = self.parse_and()

        while self.accept("LOGICAL_OPERATOR", "||"):
            right = self.parse_and()
            node = {
                "type": "binary",
                "operator": "||",
                "left": node,
                "right": right,
            }

        return node

    def parse_and(self):
        """AndExpr -> NotExpr (AND NotExpr)*"""
        node = self.parse_not()

        while self.accept("LOGICAL_OPERATOR", "&&"):
            right = self.parse_not()
            node = {
                "type": "binary",
                "operator": "&&",
                "left": node,
                "right": right,
            }

        return node

    def parse_not(self):
        """NotExpr -> NOT NotExpr | CompareExpr"""
        if self.accept("LOGICAL_OPERATOR", "!"):
            operand = self.parse_not()

            return {
                "type": "unary",
                "operator": "!",
                "operand": operand,
            }

        return self.parse_comparison()

    def parse_comparison(self):
        """CompareExpr -> Primary (RelOp Primary)?"""
        node = self.parse_primary()

        token = self.current()

        if (
            token["type"] == "RELATIONAL_OPERATOR"
            and token["lexeme"] in {">", "<", "==", "!="}
        ):
            operator = token["lexeme"]
            self.pos += 1

            right = self.parse_primary()

            node = {
                "type": "binary",
                "operator": operator,
                "left": node,
                "right": right,
            }

        return node

    def parse_primary(self):
        """
        Primary -> IDENTIFIER | NUMBER | BOOLEAN
                 | '(' Expression ')'
        """
        token = self.current()
        token_type = token["type"]
        value = token["lexeme"]

        if token_type == "IDENTIFIER":
            self.pos += 1

            if value in {"true", "false"}:
                return {
                    "type": "boolean",
                    "value": value == "true",
                }

            return {
                "type": "identifier",
                "value": value,
            }

        if token_type == "NUMBER":
            self.pos += 1
            return {
                "type": "number",
                "value": value,
            }

        if token_type == "LPAREN":
            self.pos += 1
            node = self.parse_or()
            self.expect("RPAREN")
            return node

        found = value or "end of input"

        raise SyntaxError(
            f"Expected an identifier, number, Boolean, "
            f"or '(', found '{found}'"
        )


def parse_tokens(tokens):
    """Public function for use by the Flask backend."""
    return Parser(tokens).parse()

