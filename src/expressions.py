from dataclasses import dataclass
from tokens import Token
import typing


class Expr:
    def accept(self, visitor):
        raise NotImplemented


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


@dataclass
class Literal(Expr):
    value: typing.Any

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)
