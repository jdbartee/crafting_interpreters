from dataclasses import dataclass
from expressions import Expr
import tokens
import typing


class Stmt:
    def accept(self, visitor):
        raise NotImplemented


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


@dataclass
class Var(Stmt):
    name: tokens.Token
    initializer: Expr

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)


@dataclass
class Block(Stmt):
    statements: [Stmt]

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)


@dataclass
class Function(Stmt):
    name: tokens.Token
    params: [tokens.Token]
    body: [Stmt]

    def accept(self, visitor):
        return visitor.visit_function_stmt(self)


@dataclass
class Return(Stmt):
    keyword: tokens.Token
    value: Expr

    def accept(self, visitor):
        return visitor.visit_return_stmt(self)
