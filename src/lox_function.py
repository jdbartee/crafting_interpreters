import statements as Stmt
from environment import Environment
from errors import Return
from tokens import Token, THIS

this_token = Token(THIS, "this", "this", -1)

class LoxFunction:

    def __init__(self, declaration: Stmt.Function, closure: Environment, is_initializer=False):
        self.closure = closure
        self.declaration = declaration
        self.is_initializer = is_initializer

    def call(self, interpreter, arguments):
        env = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            arg = arguments[i]
            env.define(param, arg)

        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, this_token)
            return return_value.value

        if self.is_initializer: return self.closure.get_at(0, this_token)
        return None

    def arity(self):
        return len(self.declaration.params)

    def to_string(self):
        return f"<fn {self.declaration.name.lexeme}>"

    def bind(self, instance):
        env = Environment(self.closure)
        env.define(this_token, instance)
        return LoxFunction(self.declaration, env, is_initializer=self.is_initializer)
