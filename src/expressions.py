from dataclasses import dataclass

from tokens import Token
import typing


class Expr:
    def accept(self, visitor):
        raise NotImplemented


@dataclass(frozen=True, eq=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


@dataclass(frozen=True, eq=True)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


@dataclass(frozen=True, eq=True)
class Literal(Expr):
    value: typing.Any

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


@dataclass(frozen=True, eq=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


@dataclass(frozen=True, eq=True)
class Variable(Expr):
    name: Token

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)


@dataclass(frozen=True, eq=True)
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)


@dataclass(frozen=True, eq=True)
class Logical(Binary):
    def accept(self, visitor):
        return visitor.visit_logical_expr(self)


@dataclass(frozen=True, eq=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: [Expr]

    def accept(self, visitor):
        return visitor.visit_call_expr(self)


@dataclass(frozen=True, eq=True)
class Get(Expr):
    object: Expr
    name: Token

    def accept(self, visitor):
        return visitor.visit_get_expr(self)


@dataclass(frozen=True, eq=True)
class Set(Expr):
    object: Expr
    name: Token
    value: Expr

    def accept(self, visitor):
        return visitor.visit_set_expr(self)


@dataclass(frozen=True, eq=True)
class This(Expr):
    keyword: Token

    def accept(self, visitor):
        return visitor.visit_this_expr(self)


@dataclass(frozen=True, eq=True)
class Super(Expr):
    keyword: Token
    method: Token

    def accept(self, visitor):
        return visitor.visit_super_expr(self)
