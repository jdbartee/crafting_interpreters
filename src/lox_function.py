import statements as Stmt
from environment import Environment
from errors import Return


class LoxFunction:

    def __init__(self, declaration: Stmt.Function, closure: Environment):
        self.closure = closure
        self.declaration = declaration

    def call(self, interpreter, arguments):
        env = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            arg = arguments[i]
            env.define(param, arg)

        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as return_value:
            return return_value.value
        return None

    def arity(self):
        return len(self.declaration.params)

    def to_string(self):
        return f"<fn {self.declaration.name.lexeme}>"
