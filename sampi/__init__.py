from .lexer import lex
from .parser import Parser
from .compiler import Compiler
from .vm import run_vm

def vm_run(code):
    tokens = lex(code)
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler()
    byte_code = compiler.compile_(ast)
    run_vm(byte_code)

print("Welcome to Sampi\n")
