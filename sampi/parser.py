from . import ast_nodes as a

ops = {
       "PLUS",
       "MINUS",
       "MUL",
       "DIV",
       "POWER",
       "MOD",
       "EQUALITY",
       "NOT_EQUAL",
       "LESS_EQUAL",
       "GREATER_EQUAL",
       "LESS",
       "GREATER",
       "AND",
       "OR",
       "NOT",
       "NEG",
       "IN"
       }

unary_ops = {"NOT", "NEG"}

parens = ("LBRAK", "LCURL")

binds_atom = {"NUMBER": a.Number, "STRING": a.String, "IDENT": a.Var,}

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.len = len(tokens)
        self.keywords = {
            "SET": self.set_,
            "GLUE": self.glue,
            "UNTIL": self.until,
            "IF": self.if_,
            "REPEAT": self.repeat,
            "RETURN": lambda _self=self: a.Return(self.parse_expr()),
            "FUNC": self.func,
            "EXIT": lambda: a.Exit,
            "USE": self.import_,
            "FIND": self.find,
            "CLASS": self.class_,
            "COMMENT": lambda: None,
            "BLOCK_COMMENT": lambda: None
            }

    @property
    def current(self):
        return self.tokens[self.pos]
    
    def make_literal(self, node):
        node0 = node[0]
        if node0 == "NUMBER":
            return a.Number(node[1])
        elif node0 == "STRING":
            return a.String(node[1])
        raise TypeError(f"find can only accept string or number literals, not {node0}")

    def parse_line(self):
        token = self.current
        token0 = token[0]
        if token0 in self.keywords:
            self.eat(token0)
            return self.keywords[token0]()
        else:
            return self.parse_expr()

    def _declare(self):
        name = self.eat("IDENT")[1]
        if self.current[0] == "LBRAK":
            name = self.parse_index(a.Var(name))
        self.eat("TO")
        value = self.parse_expr()
        return name, value

    def set_(self):
        return a.Set(*self._declare())
    
    def glue(self):
        return a.Glue(*self._declare())

    def if_(self):
        conds = [self.parse_expr()]
        self.eat("COLON")
        codes = [self.parse(("END", "ELSE"), "IF_BLOCK")]
        while self.current[0] == "ELSE":
            self.eat("ELSE")
            if self.current[0] == "IF":
                self.eat("IF")
                conds.append(self.parse_expr())
                self.eat("COLON")
                codes.append(self.parse(("END", "ELSE"), "IF_BLOCK"))
            else:
                self.eat("COLON")
                conds.append(a.Var("true"))
                codes.append(self.parse(("END",), "ELSE_BLOCK"))
                break
        self.eat("END")
        return a.If(conds, codes)

    def repeat(self):
        num = self.parse_expr()
        var = None
        if self.current[0] == "AS":
            self.eat("AS")
            var = self.eat("IDENT")[1]
        self.eat("COLON")
        code = self.parse("END", "REPEAT_BLOCK")
        return a.Repeat(num, code, var)

    def until(self):
        condition = self.parse_expr()
        self.eat("COLON")
        return a.Until(condition, self.parse("END", "UNTIL_BLOCK"))

    def func(self):
        name = self.eat("IDENT")[1]
        params = []
        while self.current[0] != "COLON":
            params.append(self.eat("IDENT")[1])
        self.eat("COLON")
        return a.Func(name, params, self.parse("END", "FUNCTION_BLOCK"))

    def import_(self):
        name = self.eat("IDENT")[1]
        if self.current[0] == "AS":
            self.eat("AS")
            return a.Import(name, self.eat("IDENT")[1])
        return a.Import(name, name)
    
    def find(self):
        var = a.Var(self.eat("IDENT")[1])
        self.eat("COLON")
        choices = {}
        
        while (curr := self.current)[0] in ("NUMBER", "STRING", "COLON"):
            curr0 = curr[0]

            if curr0 == "COLON":
                self.eat("COLON")
                choices[None] = self.parse(("END",), "FIND_CHOICE")
                break

            choice = [self.make_literal(curr)]
            self.eat(curr0)
        
            while self.current[0] == "OR":
                self.eat("OR")
                choice.append(self.make_literal(self.current))
                self.eat(self.current[0])
    
            self.eat("COLON")
            choices[tuple(choice)] = self.parse(("END", "NUMBER", "STRING", "COLON"), "FIND_CHOICE")
            
            if self.current == "END":
                break
        
        self.eat("END")
        return a.Find(var, choices)
    
    def class_(self):
        name = self.eat("IDENT")[1]
        parent_classes = []
        while self.current[0] != "COLON":
            parent_classes.append(self.eat("IDENT")[1])
        self.eat("COLON")
        return a.Class(name, self.parse("END", "CLASS_BLOCK"), parent_classes)
        

    def parse_multiset(self, token0):
        self.eat(token0)
        if token0 in ("LBRAK", "LPAR"):
            rparn = "R" + token0[1:]
            list_ = []
            while self.current[0] != rparn:
                nxt_item = self.parse_expr()
                if nxt_item is not None:
                    list_.append(nxt_item)
                    if self.current[0] != rparn:
                        self.eat("COMMA")
            self.eat(rparn)
            return a.Array(list_)

        elif token0 == "LCURL":
            dict_ = {}
            while self.current[0] != "RCURL":
                next_key = self.parse_expr()
                if next_key is not None:
                    self.eat("COLON")
                    next_item = self.parse_expr()
                    dict_[next_key] = next_item
                    if self.current[0] != "RCURL":
                        self.eat("COMMA")
            self.eat("RCURL")
            return a.Dict(dict_)

    def parse_index(self, ansr):
        var = ansr
        index = self.parse_multiset("LBRAK")._list()
        var = a.Index(var, index[0])
        while self.current[0] == "LBRAK":
            index = self.parse_multiset("LBRAK")._list()
            var = a.Index(var, index[0])
        return var

    def eat(self, wanted):
        token = self.current
        self.pos += 1
        if token[0] != wanted:
            raise SyntaxError(f"got {token[0]}. did you mean {wanted}?")
        return token

    def parse_atom(self):
        token = self.current
        token0, token1 = token

        if token0 in binds_atom:
            self.eat(token0)
            ansr = binds_atom[token0](token1)

            if type(ansr) is a.Var and self.current[0] == "LPAR":
                ansr = a.Call(ansr.name, self.parse_multiset(self.current[0])._list())

            if type(ansr) in {a.Var, a.String, a.Call}: # class stuff
                while self.current[0] == "DOT":
                    self.eat("DOT")
                    name = self.eat("IDENT")[1]
                    if self.current[0] == "LPAR":
                        ansr = a.MethodCall(ansr, name, self.parse_multiset(self.current[0])._list())
                    else:
                        ansr = a.Attribute(ansr, name)
                    if self.current[0] == "LBRAK":
                        ansr = self.parse_index(ansr)

            if type(ansr) in {a.Var, a.String, a.Call, a.MethodCall} and self.current[0] == "LBRAK":
                return self.parse_index(ansr)

            return ansr

        elif token0 in parens:
            ansr = self.parse_multiset(token0)
            if type(ansr) in {a.Array, a.Dict} and self.current[0] == "LBRAK":
                return self.parse_index(ansr)
            return ansr

        elif token0 == "LPAR":
            self.eat("LPAR")
            expr = self.parse_expr()
            self.eat("RPAR")
            return expr

        elif token0 in unary_ops:
            return token0

        raise SyntaxError(f"unexpected: {token}")

    def parse_expr(self): # no precedence
        left = self.parse_atom()

        while self.current[0] in ops:
            op = self.eat(self.current[0])
            if op[0] in unary_ops and left not in unary_ops:
                self.pos -= 1 # we need to get the same token again for unary ops
                return left
            right = self.parse_atom()
            if right in unary_ops:
                right = self.parse_expr()
            left = a.Op(left, op[0], right)

        return left

    def parse(self, end="EOF", type_="FILE"):
        if type(end) is tuple:
            try:
                ast = []
                while self.current[0] not in end:
                    node = self.parse_line()
                    if node is not None:
                        ast.append(node)
                return ast
            except IndexError:
                raise SyntaxError(f"missing {end} for {type_}") from None
        else:
            try:
                ast = []
                while self.current[0] != end:
                    node = self.parse_line()
                    if node is not None:
                        ast.append(node)

                self.eat(end)
                return ast
            except IndexError:
                raise SyntaxError(f"missing {end} for {type_}") from None