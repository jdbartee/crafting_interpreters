from errors import LoxRuntimeError


class Environment:
    def __init__(self, parent=None):
        self.parent: Environment = parent
        self.values = {}

    def define(self, name, value):
        self.values[name.lexeme] = value

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.parent is not None:
            return self.parent.get(name)

        raise LoxRuntimeError(name, f"Undefined Variable '{name.lexeme}'.")

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return value

        if self.parent is not None:
            return self.parent.assign(value)

        raise LoxRuntimeError(name, f"Undefined Variable '{name.lexeme}'.")
