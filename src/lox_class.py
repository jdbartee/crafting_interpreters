from errors import LoxRuntimeError
from lox_function import LoxFunction
from tokens import Token

class LoxClass:
    def __init__(self, name: Token, methods):
        self.name = name
        self.methods = methods

    def to_string(self):
        return self.name.lexeme

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method('init')
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self):
        initializer = self.find_method('init')
        if initializer is not None:
            return initializer.arity()
        return 0

    def find_method(self, name):
        return self.methods.get(name)


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields = {}

    def to_string(self):
        return f"{self.klass.to_string()} instance"

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise LoxRuntimeError(name, f"Undefined property {name.lexeme}.")

    def set(self, name, value):
        self.fields[name.lexeme] = value
