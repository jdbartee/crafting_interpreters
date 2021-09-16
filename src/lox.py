import sys

from scanner import Scanner


class Lox():

	def __init__(self):
		self.had_error = False

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
		scanner = Scanner(data, self.error)
		tokens = scanner.scan_tokens()

		for token in tokens:
			print(token)

	def error(self, line, message):
		self.report(line, "", message)

	def report(self, line, where, message):
		print("[line {}] Error{}: {}".format(line, where, message))
		self.had_error = True



if __name__ == '__main__':
	Lox().main(sys.argv[1:])