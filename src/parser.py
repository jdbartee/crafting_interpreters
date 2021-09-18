import tokens
from expressions import Binary, Grouping, Literal, Unary


class ParserError(Exception):
    pass


class Parser:

    def __init__(self, tokens, report):
        self.tokens = tokens
        self.current = 0
        self.report = report

    def match(self, *token_types):
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def check(self, token_type):
        return self.peek().token_type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().token_type == tokens.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def parse(self):
        try:
            return self.expression()
        except ParserError:
            return None

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()
        while self.match(tokens.BANG_EQUAL, tokens.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def comparison(self):
        expr = self.term()
        while self.match(tokens.GREATER,
                         tokens.GREATER_EQUAL,
                         tokens.LESS,
                         tokens.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def term(self):
        expr = self.factor()
        while self.match(tokens.PLUS, tokens.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def factor(self):
        expr = self.unary()
        while self.match(tokens.STAR, tokens.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = Binary(left=expr, operator=operator, right=right)

        return expr

    def unary(self):
        if self.match(tokens.MINUS, tokens.BANG):
            operator = self.previous()
            right = self.unary()
            return Unary(operator=operator, right=right)

        return self.primary()

    def primary(self):
        if self.match(tokens.FALSE):
            return Literal(False)
        if self.match(tokens.TRUE):
            return Literal(True)
        if self.match(tokens.NIL):
            return Literal(None)

        if self.match(tokens.NUMBER, tokens.STRING):
            return Literal(self.previous().literal)

        if self.match(tokens.LEFT_PAREN):
            expr = self.expression()
            self.consume(tokens.RIGHT_PAREN, "Expect ')' after expression")
            return Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token, message):
        self.report(token, message)
        return ParserError()

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous() == tokens.SEMICOLON:
                return
            n = self.peek().token_type
            if n in [tokens.CLASS,
                     tokens.FUN,
                     tokens.VAR,
                     tokens.FOR,
                     tokens.IF,
                     tokens.WHILE,
                     tokens.PRINT,
                     tokens.RETURN]:
                return

            self.advance()
