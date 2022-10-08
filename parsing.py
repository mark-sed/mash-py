from lark import Lark, Transformer
from lark.lexer import Token
from lark.tree import Tree
import ir
import mash_types as types
from mash import Mash
from debugging import info, debug

class Parser(Mash):
    """
    Parser class
    """

    def __init__(self, code, opts):
        """
        Constructor
        """
        self.code = code
        self.opts = opts
        with open("grammars/mash.lark", "r") as gfile:
            grammar = gfile.read()
        self.parser = Lark(grammar, start="start")
    
    def parse(self):
        """
        Parses mash code
        """
        parse_tree = self.parser.parse(self.code)
        if self.opts.verbose:
            info(parse_tree.pretty(), self.opts)
        return parse_tree

class ConstTransformer(Transformer):
    """
    Tree transformer
    """
    def __init__(self, symb_table):
        """
        Transformer constructor
        """
        self.symb_table = symb_table
        self._last_id = 0

    def uniq_var(self):
        self._last_id += 1
        return f"@ct_{self._last_id}"

    def scope_name(self, items):
        # Single variable = declaration
        if len(items) == 1:
            return items[0]
        # Scope name
        var = []
        for v in items:
            if type(v.value) == list:
                var += v.value
            else:
                var.append(v.value)
        return Token("scope_name", var)

    def int(self, items):
        return Token("SIGNED_INT", ir.Int(int(items[0].value)))

    def float(self, items):
        return Token("SIGNED_FLOAT", ir.Float(float(items[0].value)))

    def nil(self, items):
        return Token("nil", types.Nil())

    def true(self, items):
        return Token("true", types.Bool(True))

    def false(self, items):
        return Token("false", types.Bool(False))

    def string(self, items):
        return Token("string", types.String(items[0].value[1:-1]))

    def rstring(self, items):
        return Token("string", types.RString(items[0].value[1:-1]))

    def fstring(self, items):
        return Token("string", types.FString(items[0].value[1:-1]))

    def hex_int(self, items):
        return Token("SIGNED_INT", types.Int(int(items[0].value, base=16)))

    def list(self, items):
        v = []
        code = []
        for x in items:
            if x.type == "CODE":
                code += x.value
                v.append(code[-1].dst)
            else:
                v.append(x.value)
        if len(code) == 0:
            return Token("list", types.List(v))
        else:
            return Token("CALC", [Token("CODE", code), Token("list", types.List(v))])
    
    def arg_list(self, items):
        if len(items) > 2:
            return Token("arg_list", items[0].value+[(items[1].value, items[2].value)])
        else:
            return Token("arg_list", [(items[0].value, items[1].value)])

    def fun_args(self, items):
        args = []
        for x in items:
            if x.type == "arg_list":
                args += x.value
            else:
                args.append((x.value, None))
        return Token("fun_args", args)

    def _help_expr_bin(self, items, op, Cls):
        # Evaluating const expr
        if (items[0].type == "SIGNED_INT" or items[0].type == "SIGNED_FLOAT") and (items[1].type == "SIGNED_INT" 
                or items[1].type == "SIGNED_FLOAT"):
            if(items[0].type == "SIGNED_FLOAT" or items[1].type == "SIGNED_FLOAT"):
                return Token("SIGNED_FLOAT", ir.Float(op(items[0].value.value, items[1].value.value)))
            else:
                return Token("SIGNED_INT", ir.Int(op(items[0].value.value, items[1].value.value)))
        # Generating code
        insts = []
        srcs = [0, 0]
        for i in range(0, 2):
            if items[i].type == "CODE":
                insts += items[i].value
                # Expr code
                #if issubclass(type(items[i].value[-1]), ir.Expr):
                srcs[i] = items[i].value[-1].dst
            else:
                srcs[i] = items[i].value
        insts.append(Cls(srcs[0], srcs[1], self.uniq_var()))
        return Token("CODE", insts)

    def _help_expr_log(self, items, op, Cls):
        if type(items[0].value) == ir.Bool and type(items[1].value) == ir.Bool:
            r = ir.Bool(op(items[0].value.value, items[0].value.value))
            return Token(str(r), r)
        # Generating code
        insts = []
        srcs = [0, 0]
        for i in range(0, 2):
            if items[i].type == "CODE":
                insts += items[i].value
                # Expr code
                srcs[i] = items[i].value[-1].dst
            else:
                srcs[i] = items[i].value
        insts.append(Cls(srcs[0], srcs[1], self.uniq_var()))
        return Token("CODE", insts)

    def expr_mul(self, items):
        return self._help_expr_bin(items, lambda a, b: a*b, ir.Mul)

    def expr_add(self, items):
        return self._help_expr_bin(items, lambda a, b: a+b, ir.Add)

    def expr_sub(self, items):
        return self._help_expr_bin(items, lambda a, b: a-b, ir.Sub)

    def expr_or(self, items):
        return self._help_expr_log(items, lambda a, b: a or b, ir.LOr)

    def expr_and(self, items):
        return self._help_expr_bin(items, lambda a, b: a and b, ir.LAnd)
"""
    def expr_not(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_lte(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_gte(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_gt(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_lt(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_eq(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_neq(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_in(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_fdiv(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_idiv(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_mod(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_exp(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_inc(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)

    def expr_dec(self, items):
        return self._help_expr_bin(items, lambda a, b: a b, ir.)
"""