import sys

from scanner import Scanner
from parser import Parser
from interpreter import Interpreter
from ast_printer import AstPrinter
import tokens
from resolver import Resolver


class Lox:

    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.ast_printer = AstPrinter()
        self.interpreter = Interpreter(self.runtime_error)

    def main(self, args):
        if len(args) > 1:
            print("Usage: python lox.py [script]")
            sys.exit(64)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()

    def run_file(self, file):
        data = open(file, 'r').read()
        self.run(data)
        if self.had_error:
            sys.exit(65)
        if self.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            data = input("> ")
            self.run(data)
            self.had_error = False
            self.hod_runtime_error = False

    def run(self, data):
        scanner = Scanner(data, self.lexer_error)
        tokens = scanner.scan_tokens()

        if self.had_error:
            return
        parser = Parser(tokens, self.parser_error)
        statements = parser.parse()

        if self.had_error:
            return

        resolver = Resolver(self.interpreter, self.parser_error)
        resolver.resolve(*statements)

        if self.had_error:
            return
        self.interpreter.interpret(statements)

    def lexer_error(self, line, message):
        self.report(line, "", message)

    def parser_error(self, token, message):
        if token.token_type == tokens.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, " at '" + token.lexeme + "' ", message)

    def runtime_error(self, error):
        print(f"{error.message}\n[line {error.token.line}]")
        self.had_runtime_error = True

    def report(self, line, where, message):
        print("[line {}] Error{}: {}".format(line, where, message))
        self.had_error = True


if __name__ == '__main__':
    Lox().main(sys.argv[1:])
