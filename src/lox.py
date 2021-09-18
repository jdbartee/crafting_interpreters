import sys

from scanner import Scanner
from parser import Parser
from ast_printer import AstPrinter
import tokens


class Lox():

    def __init__(self):
        self.had_error = False
        self.ast_printer = AstPrinter()

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

    def run_prompt(self):
        while True:
            data = input("> ")
            self.run(data)
            self.had_error = False

    def run(self, data):
        scanner = Scanner(data, self.lexer_error)
        tokens = scanner.scan_tokens()

        if self.had_error: return
        parser = Parser(tokens, self.parser_error)
        expression = parser.parse()

        if self.had_error: return
        print(self.ast_printer.to_string(expression))



    def lexer_error(self, line, message):
        self.report(line, "", message)

    def parser_error(self, token, message):
        if token.token_type == tokens.EOF:
            self.report(token.line, "at end", message)
        else:
            self.report(token.line, " at '" + token.lexeme + "' ", message)

    def report(self, line, where, message):
        print("[line {}] Error{}: {}".format(line, where, message))
        self.had_error = True


if __name__ == '__main__':
    Lox().main(sys.argv[1:])
