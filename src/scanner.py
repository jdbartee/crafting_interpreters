import tokens

class Scanner():

    def __init__(self, source, error):
        self.had_error = False
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.length = len(source)
        self.error = error
        self.keyword_dict = {
            "and": tokens.AND,
            "class": tokens.CLASS,
            "else": tokens.ELSE,
            "false": tokens.FALSE,
            "for": tokens.FOR,
            "fun": tokens.FUN,
            "if": tokens.IF,
            "nil": tokens.NIL,
            "or": tokens.OR,
            "print": tokens.PRINT,
            "return": tokens.RETURN,
            "super": tokens.SUPER,
            "this": tokens.THIS,
            "true": tokens.TRUE,
            "var": tokens.VAR,
            "while": tokens.WHILE
        }

    def scan_tokens(self):
        self.tokens = []
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.add_eof_token()
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if False: pass
        elif c == "(": self.add_token(tokens.LEFT_PAREN, None)
        elif c == ")": self.add_token(tokens.RIGHT_PAREN, None)
        elif c == "{": self.add_token(tokens.LEFT_BRACE, None)
        elif c == "}": self.add_token(tokens.RIGHT_BRACE, None)
        elif c == ",": self.add_token(tokens.COMMA, None)
        elif c == ".": self.add_token(tokens.DOT, None)
        elif c == "-": self.add_token(tokens.MINUS, None)
        elif c == "+": self.add_token(tokens.PLUS, None)
        elif c == ":": self.add_token(tokens.COLON, None)
        elif c == ";": self.add_token(tokens.SEMICOLON, None)
        elif c == "*": self.add_token(tokens.STAR, None)
        elif c == "!":
            if self.match("="):
                self.add_token(tokens.BANG_EQUAL, None)
            else:
                self.add_token(tokens.BANG, None)
        elif c == "=":
            if self.match("="):
                self.add_token(tokens.EQUAL_EQUAL, None)
            else:
                self.add_token(tokens.EQUAL, None)
        elif c == "<":
            if self.match("="):
                self.add_token(tokens.LESS_EQUAL, None)
            else:
                self.add_token(tokens.LESS, None)
        elif c == ">":
            if self.match("="):
                self.add_token(tokens.GREATER_EQUAL, None)
            else:
                self.add_token(tokens.GREATER)
        elif c == "/":
            if self.match("/"):
                while (not self.is_at_end() and self.peek() != "\n"):
                    self.advance()
            else:
                self.add_token(tokens.SLASH, None)
        elif c == " " or c == "\t" or c == "\r": pass
        elif c == "\n": self.line += 1
        elif c == '"': self.string()
        elif c.isdigit(): self.number()
        elif self.is_alpha(c): self.identifier()
        else:
            self.error(self.line, "Unexpected Character.")

    def identifier(self):
        while self.is_alphanum(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        token_type = self.keyword_dict.get(text, tokens.IDENTIFIER)
        self.add_token(token_type, None)

    def string(self):
        while (not self.is_at_end()) and self.peek() != '"':
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error(self.line, "Unterminated string.")
            return

        self.advance()

        value = self.source[self.start + 1:self.current - 1]
        self.add_token(tokens.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()

        while self.peek().isdigit():
            self.advance()

        value = self.source[self.start:self.current]
        self.add_token(tokens.NUMBER, float(value))

    def is_alpha(self, c):
        import re
        return re.match(r"[_a-zA-Z]", c)

    def is_alphanum(self, c):
        return c.isdigit() or self.is_alpha(c)

    def match(self, c):
        if self.is_at_end(): return False

        if c == self.source[self.current]:
            self.current += 1
            return True

        return False

    def peek(self):
        if self.is_at_end(): return "\0"
        return self.source[self.current]

    def peek_next(self):
        if (self.current + 1 >= self.length): return "\0"
        return self.source[self.current + 1]

    def advance(self):
        c = self.source[self.current]
        self.current += 1
        return c

    def add_token(self, token_type, literal):
        text = self.source[self.start: self.current]
        self.tokens.append(tokens.Token(token_type, text, literal, self.line))

    def add_eof_token(self):
        self.tokens.append(tokens.Token(tokens.EOF, "", "", self.line))

    def is_at_end(self):
        return self.current >= self.length