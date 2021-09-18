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
