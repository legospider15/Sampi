from . import errors
from .lexer import lex
from .parser import Parser
from .compiler import Compiler
from .ast_nodes import String, Number, Array, Dict, Index
from pathlib import Path
import operator
import random
import importlib.util as importer

def add(a, b):
    ta = type(a)
    tb = type(b)

    if ta in (String, Number) and tb in (String, Number):
        if ta is String or tb is String:
            return f"{a}{b}"
    return a + b

def div(a, b):
    if b == 0:
        raise ZeroDivisionError("You cannot divided by 0")
    ansr = a / b
    if ansr.is_integer():
        return int(ansr)
    return ansr

def in_(item, iter_):
    return item in iter_

def sgn(x):
    return (x > 0) - (x < 0)

STANDARED_LIBRARY = {"math", "lines"}

PATH = __file__.rsplit("/", 1)[0] + "/"
DOWNLOADS = Path.home() / "Downloads"

BINARY_OPS = {
    "PLUS": add,
    "MINUS": operator.sub,
    "MUL": operator.mul,
    "DIV": div,
    "POWER": operator.pow,
    "MOD": operator.mod,

    "EQUALITY": operator.eq,
    "NOT_EQUAL": operator.ne,
    "LESS": operator.lt,
    "GREATER": operator.gt,
    "LESS_EQUAL": operator.le,
    "GREATER_EQUAL": operator.ge,

    "AND": operator.and_,
    "OR": operator.or_,
    "IN": in_
}

UNARY_OPS = {
    "NOT": operator.not_,
    "NEG": operator.neg
    }

def ask(prompt=""):
    return String(input(prompt))

def random_(a, b):
    return Number(random.randint(a, b))

def run_vm(byte_code, starting_vars=None, starting_glues=None, type_="START"):
    stack = []
    glues = starting_glues or set()
    vars_ = {"true": True, 
            "false": False, 
            "none": None,

            "say": print,
            "ask": ask,
            "abs": abs,
            "sgn": sgn,
            "min": min,
            "max": max,
            "random": random_,
            "len": len,
            
            "string": String,
            "number": Number
             } | (starting_vars or {})

    def get_bytes(num):
        if num == 0:
            return []
        bytes_ = stack[-num:]
        del stack[-num:]
        return bytes_
    
    def is_glued(name):
        if name in glues:
            raise errors.GlueError(f"{name!r} is glued")
    
    def resolve_parent(node):
        indices = []

        while type(node) is Index:
            indices.append(node.index)
            node = node.var

        indices.reverse()
        node = vars_[node.name]

        for i in indices[:-1]:
            if type(node) is Array and i > 0:
                i -= 1
            node = node[i]
        last = indices[-1]
        if type(node) is Array and last > 0:
            last -= 1
        return node, last

    ip = 0
    len_ = len(byte_code)

    while ip < len_:
        byte = byte_code[ip]
        op = byte[0]
        
        if (value := BINARY_OPS.get(op)) is not None:
            right = stack.pop()
            left = stack.pop()
            stack.append(value(left, right))

        elif (value := UNARY_OPS.get(op)) is not None:
            top = stack.pop()
            stack.append(value(top))

        else:
            match op:
                case "STORE":
                    name = byte[1]
                    if type(name) is Index:
                        parent, index = resolve_parent(name)
                        parent[index] = stack.pop()
                    else:
                        is_glued(name)
                        vars_[name] = stack.pop()
                
                case "GLUE":
                    name = byte[1]
                    is_glued(name)
                    if type(name) is Index:
                        raise errors.GlueError("you cannot glue indices")
                    if name in vars_:
                        raise errors.GlueError(f"{name!r} is already defined")
                    vars_[name] = stack.pop()
                    glues.add(name)
                    
                case "CONST":
                    stack.append(byte[1])
    
                case "GET":
                    try:
                        stack.append(vars_[byte[1]])
                    except KeyError:
                        raise NameError(f"'{byte[1]}' is undefined") from None
                
                case "CALL":
                    args = get_bytes(byte[2])
                    name = byte[1]
                    stack.append(vars_[name](*args))
    
                case "JUMP_IF_FALSE":
                    if not stack.pop():
                        ip = byte[1]
                        continue
                
                case  "JUMP_IF_TRUE":
                    if stack.pop():
                        ip = byte[1]
                        continue
                
                case "JUMP":
                    ip = byte[1]
                    continue

                case "INIT_LOOP":
                    loop = byte[1]
                    vars_[f"!{loop}"] = 0
                    multiset = stack.pop()
                    if type(multiset) is Number:
                        vars_[f"${loop}"] = range(multiset + 1)
                    else:
                        vars_[f"${loop}"] = multiset

                case "LOOP_NEXT":
                    loop = byte[2]
                    loop_var = f"!{loop}"
                    multiset = vars_[f"${loop}"]
                    current_loop = vars_[loop_var]
    
                    if current_loop < len(multiset) - (type(multiset) is range):
                        next_loop = current_loop + 1
                        vars_[loop_var] = next_loop
                    
                        if (var := byte[3]):
                            vars_[var] = multiset[next_loop]
                    else:
                        ip = byte[1]
                        continue

                case "START_FUNC":
                    ip += 1
                    code = []
                    name = byte[1]
                    is_glued(name)
                    while (byte := byte_code[ip])[0] != "END_FUNC":
                        code.append(byte)
                        ip += 1
                    vars_[name] = Function(code, byte[1], vars_, glues, name)

                case "RETURN":
                    if type_ == "START":
                        raise SyntaxError("return appeared outsied a function")
                    return stack[-1]
    
                case "INDEX":
                    index = stack.pop()
                    var = stack.pop()
                    stack.append(var[index])
                
                case "IMPORT":
                    name = byte[2]
                    is_glued(name)
                    vars_[name] = Module(byte[1])
                
                case "ATTRIBUTE":
                    stack.append(stack.pop().attributes[byte[1]])
                
                case "METHOD_CALL":
                    args = get_bytes(byte[2])
                    obj = stack.pop()
                    name = byte[1]
                    stack.append(obj.attributes[name](*args))
                
                case "ARRAY":
                    stack.append(Array(get_bytes(byte[1])))
                
                case "DICT":
                    items = get_bytes(byte[1] * 2)
                    stack.append(Dict(dict(zip(items[::2], items[1::2]))))

        ip += 1
    if type_ == "START":
        return vars_

class Function:
    def __init__(self, byte_code, params, vars_, glues, name):
        self.byte_code = byte_code
        self.params = params
        self.vars_ = vars_
        self.glues = glues
        self.name = name

    def __call__(self, *args):
        return run_vm(self.byte_code, self.vars_ | dict(zip(self.params, args)), self.glues, "CALL")
    
    def __repr__(self):
        return f"function {self.name}"

class Module:
    def __init__(self, name, directory=DOWNLOADS):
        if name in STANDARED_LIBRARY:
            spec = importer.spec_from_file_location(name, f"{PATH}standard_library/{name}.py")
            module = importer.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self.attributes = vars(module)["new_vars"]
        else:
            with open(f"{directory}/{name}.sampi") as file:
                code = file.read()
            # lex, parse, compile, and run the module
            self.attributes = run_vm(Compiler().compile_(Parser(lex(code)).parse()))
        self.name = name
    
    def __repr__(self):
        return f"moudle {self.name}"
