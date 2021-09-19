from errors import LoxRuntimeError


class Environment:
    def __init__(self, parent=None):
        self.parent: Environment = parent
        self.values = {}

    def ancestor(self, distance):
        e = self
        for i in range(0, distance):
            e = e.parent

        return e

    def define(self, name, value):
        self.values[name.lexeme] = value

    def get(self, name, fallback=True):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if fallback and self.parent is not None:
            return self.parent.get(name)

        raise LoxRuntimeError(name, f"Undefined Variable '{name.lexeme}'.")

    def get_at(self, distance, name):
        return self.ancestor(distance).get(name, fallback=False)

    def assign(self, name, value, fallback=True):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return value

        if fallback and self.parent is not None:
            return self.parent.assign(name, value)

        raise LoxRuntimeError(name, f"Undefined Variable '{name.lexeme}'.")

    def assign_at(self, distance, name, value):
        self.ancestor(distance).assign(name, value, fallback=False)
