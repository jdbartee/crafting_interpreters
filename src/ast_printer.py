from expressions import Binary, Unary, Literal, Grouping
import tokens

class AstPrinter:

    def to_string(self, expr):
        s = expr.accept(self)
        return s

    def sexp(self, car, *cdr):
        s = f"({car}"
        for expr in cdr:
            s += " "
            s += self.to_string(expr)
        s += ")"
        return s

    def visit_binary_expr(self, expr: Binary):
        return self.sexp(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self.sexp("group", expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary):
        return self.sexp(expr.operator.lexeme, expr.right)


if __name__ == "__main__":
    expression = Binary(
        left=Unary(
            operator=tokens.Token(tokens.MINUS, "-", "-", 1),
            right=Literal(value="123")),
        operator=tokens.Token(tokens.STAR, "*", "*", 1),
        right=Grouping(
            expression=Literal("45.67")))

    print(AstPrinter().to_string(expression))
