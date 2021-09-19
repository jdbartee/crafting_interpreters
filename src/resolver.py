from interpreter import Interpreter
from tokens import Token
import statements as Stmt
import expressions as Expr


class Resolver:

    def __init__(self, interpreter: Interpreter, report):
        self.interpreter = interpreter
        self.scopes = []
        self.report = report
        self.in_function = None
        self.in_class = None

    def resolve(self, *statements):
        for statement in statements:
            statement.accept(self)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop(-1)

    def declare(self, name):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]

        if name.lexeme in scope:
            self.report(name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False

    def define(self, name):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token):
        for (i, scope) in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
                return

    def resolve_function(self, stmt: Stmt.Function, function_type):
        enclosing = self.in_function
        self.in_function = function_type
        self.begin_scope()
        for param in stmt.params:
            self.declare(param)
            self.define(param)

        self.resolve(*stmt.body)
        self.end_scope()
        self.in_function = enclosing

    def visit_block_stmt(self, stmt: Stmt.Block):
        self.begin_scope()
        self.resolve(*stmt.statements)
        self.end_scope()

    def visit_expression_stmt(self, stmt: Stmt.Expression):
        self.resolve(stmt.expression)

    def visit_if_stmt(self, stmt: Stmt.If):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Stmt.Print):
        if stmt.expression is not None:
            self.resolve(stmt.expression)

    def visit_while_stmt(self, stmt: Stmt.While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_return_stmt(self, stmt: Stmt.Return):
        if self.in_function is None:
            self.report(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            if self.in_function == 3:
                self.resolve(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(stmt.value)

    def visit_class_stmt(self, stmt: Stmt.Class):
        enclosing = self.in_class
        self.in_class = 1
        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None:
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                self.report(stmt.superclass.name, "A class can't inherit from itself.")
            self.in_class = 2
            self.resolve(stmt.superclass)

        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]['super'] = True

        self.begin_scope()
        self.scopes[-1]['this'] = True

        for method in stmt.methods:
            declaration = 2
            if method.name.lexeme == "init":
                declaration = 3
            self.resolve_function(method, declaration)

        self.end_scope()

        if stmt.superclass is not None:
            self.end_scope()

        self.in_class = enclosing

    def visit_var_stmt(self, stmt: Stmt.Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)

        self.define(stmt.name)

    def visit_function_stmt(self, stmt: Stmt.Function):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, 1)

    def visit_assign_expr(self, expr: Expr.Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: Expr.Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr: Expr.Call):
        self.resolve(expr.callee)
        self.resolve(*expr.arguments)

    def visit_grouping_expr(self, expr: Expr.Grouping):
        self.resolve(expr.expression)

    def visit_literal_expr(self, expr: Expr.Literal):
        return

    def visit_logical_expr(self, expr: Expr.Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr: Expr.Unary):
        self.resolve(expr.right)

    def visit_variable_expr(self, expr: Expr.Variable):
        try:
            if len(self.scopes) != 0 and self.scopes[-1].get(expr.name.lexeme) is False:
                self.report(expr.name, "Can't read local variable in it's own initializer.")
        except Exception as e:
            print(self.scopes)
            print(self.scopes[-1])
            raise e

        self.resolve_local(expr, expr.name)

    def visit_get_expr(self, expr: Expr.Get):
        self.resolve(expr.object)

    def visit_set_expr(self, expr: Expr.Set):
        self.resolve(expr.value)
        self.resolve(expr.object)

    def visit_this_expr(self, expr: Expr.This):
        if self.in_class is None:
            self.report(expr.keyword, "Can't use 'this' outside of a class")
            return None
        self.resolve_local(expr, expr.keyword)

    def visit_super_expr(self, expr: Expr.Super):
        if self.in_class is None:
            self.report(expr.keyword, "Can't use 'super' outside of a class.")
        if self.in_class != 2:
            self.report(expr.keyword, "Can't use 'super' in a class with no superclass.")

        self.resolve_local(expr, expr.keyword)
