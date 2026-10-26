# data types (not really AST)

class String(str):
    def __new__(cls, value=""):
        obj = super().__new__(cls, value)
        obj.attributes = {
            "trim": obj.strip,
            "remove": obj.remove,
            "upper": obj.upper,
            "lower": obj.lower,
            "capital": obj.capitalize,
            "title": obj.title,
            }
        return obj

    def remove(self, char):
        return self.replace(char, "")

    def __repr__(self):
        return f'"{self}"'
    
    def __str__(self):
        return  str.__str__(self)
    
    def __add__(self, o):
        return String(str.__add__(self, o))
    
    def __getitem__(self, i):
        if i > 0:
            return str.__getitem__(self, i - 1)
        return str.__getitem__(self, i)
    
class Number(float):
    def __new__(cls, value=0):
        obj = super().__new__(cls, value)
        obj.attributes = {"is_interger": obj.is_integer}
        return obj

    def __repr__(self):
        return str(int(self)) if self.is_integer() else str(self)
    
    def __add__(self, o):
        return Number(float.__add__(self, o))
    
    def __sub__(self, o):
        return Number(float.__sub__(self, o))
    
    def __mul__(self, o):
        return Number(float.__mul__(self, o))
    
    def __truediv__(self, o):
        return Number(float.__truediv__(self, o))
    
    def __pow__(self, o):
        ansr = float.__pow__(self, o)
        if type(ansr) is complex:
            raise NotImplementedError("complex numbers are not yet supported")
        return Number(ansr)
    
    def __mod__(self, o):
        return Number(float.__mod__(self, o))
    
    def __neg__(self):
        return Number(float.__neg__(self))
    
    def __index__(self):
        return int(self)
    
    def __len__(self):
        return len(float.__repr__(self)) - 1 - self.is_integer()

class Array(list):
    def __init__(self, items=()):
        super().__init__(items)
        self.attributes = {
            "add": self.append,
            "remove": self.remove,
            "delete": self.delete,
            "get_index": self.index,
            "insert": self._insert,
            "clear": self.clear,
            "join": self.join
            }

    def delete(self, index):
        if index > 0:
            index -= 1
        del self[int(index)]
    
    def _insert(self, index, value):
        if index > 0:
            index -= 1
        self.insert(index, value)
    
    def join(self, text=""):
        try:
            return String(f"{text}".join(self))
        except TypeError:
            raise TypeError("Can only join an array of strings")
            
    def __add__(self, o):
        return Array(list.__add__(self, o))

    def _list(self):
        return self
    
    def __hash__(self):
        return hash(tuple(self))
    
    def __getitem__(self, i):
        if i > 0:
            return list.__getitem__(self, i - 1)
        return list.__getitem__(self, i)
    
class Dict(dict):
    def __init__(self, items=()):
        super().__init__(items)
        self.attributes = {
            "add": self.add,
            "get_default": self.get,
            "add_default": self.add_default,
            "clear": self.clear,
            "add_error": self.add_error,
            "keys": lambda: Array(self.keys()),
            "values": lambda: Array(self.values()),
            "remove": self.pop
            }

    def add(self, key, value):
        self[key] = value

    def add_default(self, key, value):
        self.setdefault(key, value)

    def add_error(self, key, value):
        if key in self:
            raise KeyError(f"key {key!r} already exists")
        self[key] = value
    
    def __add__(self, o):
        return Dict(self.__or__(o))

# misc. (these are AST)


class Index:
    def __init__(self, var, index):
        self.var = var
        self.index = index

    def __repr__(self):
        return f"{self.var}[{self.index}]"

class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.name}({self.args})"

class MethodCall(Call):
    def __init__(self, obj, name, args):
        super().__init__(name, args)
        self.obj = obj

    def __repr__(self):
        return f"{self.obj}.{self.name}({self.args})"

class Var:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Attribute(Var):
    def __init__(self, obj, name):
        super().__init__(name)
        self.obj = obj

    def __repr__(self):
        return f"{self.obj}.{self.name}"

class Op:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"

# keywords

class Find:
    def __init__(self, var, choices):
        self.var = var
        self.choices = choices
    
    def __repr__(self):
        return f"find {self.var}: {self.choices}"

class Return:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"return {self.value}"

class Exit:
    def __init__(self):
        pass

    def __repr__(self):
        return "exit"

class Set:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"set {self.name} to {self.value}"

class Glue:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"glue {self.name} to {self.value}"

class If:
    def __init__(self, conds, codes):
        self.conds = conds
        self.codes = codes

    def __repr__(self):
        return f"{self.conds} {self.codes}"

class Repeat:
    def __init__(self, num, code, var):
        self.num = num
        self.code = code
        self.var = var

    def __repr__(self):
        return f"repeat {self.num} as {self.var} {self.code}"

class Until:
    def __init__(self, cond, code):
        self.cond = cond
        self.code = code

    def __repr__(self):
        return f"until {self.cond} {self.code}"

class Func:
    def __init__(self, name, params, code):
        self.name = name
        self.params = params
        self.code = code

    def __repr__(self):
        return f"func {self.name} {self.params} {self.code}"

class Import:
    def __init__(self, name, alias):
        self.name = name
        self.alias = alias

    def __repr__(self):
        return f"import {self.name} as {self.alias}"
