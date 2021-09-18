
class LoxRuntimeError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message


class Return(Exception):
    def __init__(self, value):
        self.value = value


class ParserError(Exception):
    pass