import tokens
from environment import Environment
from errors import LoxRuntimeError, Return

import statements as Stmt
import expressions as Expr
from src.lox_function import LoxFunction


class CLOCK:

    @staticmethod
    def arity():
        return 0

    @staticmethod
    def call(interpreter, arguments):
        import datetime
        return float(datetime.datetime.now().timestamp())

    @staticmethod
    def to_string():
        return "<native fn clock>"


class PRINT:
    @staticmethod
    def arity():
        return 1

    @staticmethod
    def call(interpreter, arguments):
        value = arguments[0]
        if hasattr(value, "to_string") and callable(value.to_string):
            value = value.to_string()
        print(value)
        return None

    def to_string(self):
        return "<native fn print>"


class Interpreter:
    def __init__(self, report):
        self.report = report
        self.global_env = Environment()
        self.environment = self.global_env

        self.global_env.define(tokens.Token(tokens.IDENTIFIER, "clock", "clock", -1), CLOCK)
        self.global_env.define(tokens.Token(tokens.IDENTIFIER, "print", "print", -1), PRINT)

    def interpret(self, stmts: [Stmt.Stmt]):
        try:
            for stmt in stmts:
                self.execute(stmt)
        except LoxRuntimeError as ir:
            self.report(ir)

    def execute(self, stmt: Stmt.Stmt):
        return stmt.accept(self)

    def evaluate(self, expr: Expr.Expr):
        return expr.accept(self)

    def visit_block_stmt(self, stmt: Stmt.Block):
        return self.execute_block(
            stmt.statements,
            Environment(self.environment))

    def execute_block(self, stmts: [Stmt], env: Environment):
        prev_environment = self.environment
        try:
            self.environment = env
            for stmt in stmts:
                self.execute(stmt)
        finally:
            self.environment = prev_environment
        return None


    def visit_print_stmt(self, stmt: Stmt.Print):
        value = self.evaluate(stmt.expression)
        if hasattr(value, "to_string") and callable(value.to_string):
            value = value.to_string()

        print(value)
        return None

    def visit_expression_stmt(self, stmt: Stmt.Expression):
        self.evaluate(stmt.expression)
        return None

    def visit_if_stmt(self, stmt: Stmt.If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_var_stmt(self, stmt: Stmt.Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name, value)

    def visit_while_stmt(self, stmt: Stmt.While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def visit_function_stmt(self, stmt: Stmt.Function):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name, function)
        return None

    def visit_return_stmt(self, stmt: Stmt.Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise Return(value)

    def visit_binary_expr(self, expr: Expr.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.token_type == tokens.MINUS:
            self.check_numeric_operands(expr.operator, left, right)
            return left - right
        if expr.operator.token_type == tokens.PLUS:
            if type(left) != type(right):
                raise LoxRuntimeError(
                    expr.operator,
                    "Operands must both be either strings or numbers")
            if type(left) is not str and type(left) is not float:
                raise LoxRuntimeError(
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

    def visit_grouping_expr(self, expr: Expr.Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: Expr.Literal):
        return expr.value

    def visit_unary_expr(self, expr: Expr.Unary):
        right = self.evaluate(expr.right)
        if expr.operator.token_type == tokens.MINUS:
            self.check_numeric_operands(expr.operator, right)
            return -right
        if expr.operator.token_type == tokens.BANG:
            return not self.is_truthy(right)

        return None

    def visit_assign_expr(self, expr: Expr.Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_variable_expr(self, expr: Expr.Variable):
        return self.environment.get(expr.name)

    def visit_logical_expr(self, expr: Expr.Logical):
        left = self.evaluate(expr.left)

        if expr.operator.token_type == tokens.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_call_expr(self, expr: Expr.Call):
        callee = self.evaluate(expr.callee)
        arguments = []
        for arg in expr.arguments:
            arguments.append(self.evaluate(arg))

        if not hasattr(callee, "call") or not callable(callee.call):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise LoxRuntimeError(expr.paren, "Wrong number of arguments.")

        return callee.call(self, arguments)

    def is_truthy(self, value):
        return value is not None and value is not False

    def is_equal(self, left, right):
        return left == right

    def check_numeric_operands(self, operator, *operands):
        for operand in operands:
            if type(operand) is not float:
                raise LoxRuntimeError(operator, "Operand must be a number.")
