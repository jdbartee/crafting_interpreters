import tokens


class InterpreterError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message


class Interpreter:
    def __init__(self, report):
        self.report = report

    def interpret(self, expr):
        try:
            value = self.evaluate(expr)
            print(value)
        except InterpreterError as ir:
            self.report(ir)

    def evaluate(self, expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.token_type == tokens.MINUS:
            self.check_numeric_operands(expr.operator, left, right)
            return left - right
        if expr.operator.token_type == tokens.PLUS:
            if type(left) != type(right):
                raise InterpreterError(
                    expr.operator,
                    "Operands must both be either strings or numbers")
            if type(left) is not str and type(left) is not float:
                raise InterpreterError(
                    expr.operator,
                    "Operands must both be either strings or numbers")
            return left + right
        if expr.operator.token_type == tokens.STAR:
            self.check_numeric_operands(expr.operator, left, right)
            return left * right
        if expr.operator.token_type == tokens.SLASH:
            self.check_numeric_operands(expr.operator, left, right)
            return left / right
        if expr.operator.token_type == tokens.GREATER:
            self.check_numeric_operands(expr.operator, left, right)
            return left > right
        if expr.operator.token_type == tokens.GREATER_EQUAL:
            self.check_numeric_operands(expr.operator, left, right)
            return left >= right
        if expr.operator.token_type == tokens.LESS:
            self.check_numeric_operands(expr.operator, left, right)
            return left < right
        if expr.operator.token_type == tokens.LESS_EQUAL:
            self.check_numeric_operands(expr.operator, left, right)
            return left <= right
        if expr.operator.token_type == tokens.EQUAL_EQUAL:
            return self.is_equal(left, right)
        if expr.operator.token_type == tokens.BANG_EQUAL:
            return not self.is_equal(left, right)

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)
        if expr.operator.token_type == tokens.MINUS:
            self.check_numeric_operands(expr.operator, right)
            return -(right)
        if expr.operator.token_type == tokens.BANG:
            return not self.is_truthy(right)

        return None

    def is_truthy(self, value):
        return value is not None and value is not False

    def is_equal(self, left, right):
        return left == right

    def check_numeric_operands(self, operator, *operands):
        for operand in operands:
            if type(operand) is not float:
                raise InterpreterError(operator, "Operand must be a number.")
