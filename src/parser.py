import tokens
import expressions as Expr
import statements as Stmt
from errors import ParserError


class Parser:

    def __init__(self, tokens, report):
        self.tokens = tokens
        self.current = 0
        self.report = report

    def parse(self):
        statements = []
        try:
            while not self.is_at_end():
                statements.append(self.declaration())
        except ParserError:
            return None
        return statements

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

    def declaration(self):
        try:
            if self.match(tokens.VAR): return self.var_declaration()
            if self.match(tokens.CLASS): return self.class_declaration()
            if self.match(tokens.FUN): return  self.fun_declaration("function")
            return self.statement()
        except ParserError:
            self.synchronize()
            return None

    def var_declaration(self):
        name = self.consume(tokens.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(tokens.EQUAL):
            initializer = self.expression()

        self.consume(tokens.SEMICOLON, "Expect ';' after statement")
        return Stmt.Var(name, initializer)

    def class_declaration(self):
        name = self.consume(tokens.IDENTIFIER, "Expect class name.")
        superclass = None
        if self.match(tokens.LESS):
            superclass_name = self.consume(tokens.IDENTIFIER, "Expect superclass name.")
            superclass = Expr.Variable(superclass_name)
        self.consume(tokens.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(tokens.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.fun_declaration("method"))

        self.consume(tokens.RIGHT_BRACE, "Expect '}' after class body")

        return Stmt.Class(name, superclass, methods)

    def fun_declaration(self, kind):
        name = self.consume(tokens.IDENTIFIER, f"Expect {kind} name.")
        self.consume(tokens.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(tokens.RIGHT_PAREN):
            matched = True
            while matched:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters")
                parameters.append(self.consume(tokens.IDENTIFIER, "Expect parameter name."))
                matched = self.match(tokens.COMMA)
        self.consume(tokens.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(tokens.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block_statement().statements
        return Stmt.Function(name, parameters, body)

    def statement(self):
        if self.match(tokens.IF):
            return self.if_statement()
        if self.match(tokens.PRINT):
            return self.print_statement()
        if self.match(tokens.RETURN):
            return self.return_statement()
        if self.match(tokens.WHILE):
            return self.while_statement()
        if self.match(tokens.FOR):
            return self.for_statement()
        if self.match(tokens.LEFT_BRACE):
            return self.block_statement()
        return self.expression_statement()

    def if_statement(self):
        self.consume(tokens.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(tokens.RIGHT_PAREN, "Expect ')' after condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(tokens.ELSE):
            else_branch = self.statement()

        return Stmt.If(condition, then_branch, else_branch)

    def block_statement(self):
        statements = []
        while not self.check(tokens.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(tokens.RIGHT_BRACE, "Expect '}' at end of block.")
        return Stmt.Block(statements)

    def expression_statement(self):
        expr = self.expression()
        self.consume(tokens.SEMICOLON, "Expect a ';' at end of statement.")
        return Stmt.Expression(expr)

    def print_statement(self):
        value = self.expression()
        self.consume(tokens.SEMICOLON, "Expect a ';' at end of statement.")
        return Stmt.Print(value)

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(tokens.SEMICOLON):
            value = self.expression()

        self.consume(tokens.SEMICOLON, "Expect ';' after return value.")
        return Stmt.Return(keyword, value)

    def while_statement(self):
        self.consume(tokens.LEFT_PAREN, "Expect '(' after 'while'")
        condition = self.expression()
        self.consume(tokens.RIGHT_PAREN, "Expect ')' after condition")
        statement = self.statement()

        return Stmt.While(condition, statement)

    def for_statement(self):
        self.consume(tokens.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.match(tokens.SEMICOLON):
            pass
        elif self.match(tokens.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if self.match(tokens.SEMICOLON):
            pass
        else:
            condition = self.expression()
        self.consume(tokens.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if self.match(tokens.LEFT_PAREN):
            pass
        else:
            increment = self.expression()
        self.consume(tokens.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = Stmt.Block([body, Stmt.Expression(increment)])

        if condition is not None:
            body = Stmt.While(condition, body)

        if initializer is not None:
            body = Stmt.Block([initializer, body])

        return body

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logical_or()

        if self.match(tokens.EQUAL):
            equals = self.previous()
            value = self.assignment()
            name = expr.name

            if isinstance(expr, Expr.Variable):
                return Expr.Assign(name, value)
            elif isinstance(expr, Expr.Get):
                return Expr.Set(expr.object, name, value)

            self.error(equals, "Invalid Assignment Target")

        return expr

    def logical_or(self):
        expr = self.logical_and()

        while self.match(tokens.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def logical_and(self):
        expr = self.equality()

        while self.match(tokens.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(tokens.BANG_EQUAL, tokens.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def comparison(self):
        expr = self.term()
        while self.match(tokens.GREATER,
                         tokens.GREATER_EQUAL,
                         tokens.LESS,
                         tokens.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def term(self):
        expr = self.factor()
        while self.match(tokens.PLUS, tokens.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def factor(self):
        expr = self.unary()
        while self.match(tokens.STAR, tokens.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def unary(self):
        if self.match(tokens.MINUS, tokens.BANG):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator=operator, right=right)

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(tokens.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(tokens.DOT):
                name = self.consume(tokens.IDENTIFIER, "Expect property name after '.")
                expr = Expr.Get(expr, name)
            else:
                break

        return expr

    def finish_call(self, expr: Expr):
        arguments = []
        if not self.check(tokens.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(tokens.COMMA):
                arguments.append(self.expression())
                if len(arguments) >= 255:
                    self.error(self.previous(), "Can't have more than 255 arguments")
        paren = self.consume(tokens.RIGHT_PAREN, "Expect ')' after arguments.")

        return Expr.Call(expr, paren, arguments)

    def primary(self):
        if self.match(tokens.FALSE):
            return Expr.Literal(False)
        if self.match(tokens.TRUE):
            return Expr.Literal(True)
        if self.match(tokens.NIL):
            return Expr.Literal(None)
        if self.match(tokens.NUMBER, tokens.STRING):
            return Expr.Literal(self.previous().literal)
        if self.match(tokens.SUPER):
            keyword = self.previous()
            self.consume(tokens.DOT, "Expect '.' after 'super'.")
            method = self.consume(tokens.IDENTIFIER, "Expect superclass method name.")
            return Expr.Super(keyword, method)
        if self.match(tokens.THIS):
            return Expr.This(self.previous())
        if self.match(tokens.IDENTIFIER):
            return Expr.Variable(self.previous())

        if self.match(tokens.LEFT_PAREN):
            expr = self.expression()
            self.consume(tokens.RIGHT_PAREN, "Expect ')' after expression")
            return Expr.Grouping(expr)

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
