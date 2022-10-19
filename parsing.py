from lark import Lark, Transformer
from lark.lexer import Token
from lark.tree import Tree
import ir
import mash_types as types
from mash import Mash
from debugging import info, debug
import mash_exceptions as mex
from symbol_table import SymbTable

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
        return f"$ct_{self._last_id}"

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
            if type(x) == Token:
                if x.type == "CODE":
                    code += x.value
                    v.append(code[-1].dst)
                elif x.type == "CALC":
                    code += x.value[0].value
                    d = self.uniq_var()
                    val = x.value[1].value.get_value()
                    code.append(ir.AssignVar(d, types.List(val)))
                    v.append(d)
                else:
                    v.append(x.value)
            else:
                d = self.uniq_var()
                code += [items[0], ir.AssignVar(d, SymbTable.RETURN_NAME)]
                v.append(d)
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

    def arg_list_call_exp(self, items):
        i1 = items[0].value if type(items[0]) == Token else items[0]
        i2 = items[1].value if type(items[1]) == Token else items[1]
        i3 = items[2] if len(items) > 2 else None
        if i3 is not None and type(i3) == Token:
            i3 = i3.value
        if len(items) > 2:
            return Token("arg_list_call_exp", i1+[(i2, i3)])
        else:
            return Token("arg_list_call_exp", [(i1, i2)])

    def fun_call_args(self, items):
        args = []
        for x in items:
            if type(x) == Token:
                if x.type == "arg_list_call_exp":
                    args += x.value
                else:
                    args.append(x.value)
            else:
                args.append(x)
        return Token("fun_call_args", args)

    def dict(self, items):
        v = []
        code = []
        i = 0
        while i < len(items):
            x = items[i]
            y = items[i+1]
            if type(x) == Token:
                if x.type == "CODE":
                    code += x.value
                    x = code[-1].dst
                elif x.type == "CALC":
                    code += x.value[0].value
                    d = self.uniq_var()
                    val = x.value[1].value
                    code.append(ir.AssignVar(d, val))
                    x = d
                else:
                    x = x.value
            else:
                d = self.uniq_var()
                code += [items[0], ir.AssignVar(d, SymbTable.RETURN_NAME)]
                x = d
            if type(y) == Token:
                if y.type == "CODE":
                    code += y.value
                    y = code[-1].dst
                elif y.type == "CALC":
                    code += y.value[0].value
                    d = self.uniq_var()
                    val = y.value[1].value
                    code.append(ir.AssignVar(d, val))
                    y = d
                else:
                    y = y.value
            else:
                d = self.uniq_var()
                code += [items[0], ir.AssignVar(d, SymbTable.RETURN_NAME)]
                y = d
            i += 2
            v.append((x, y))
        if len(code) == 0:
            return Token("dict", types.Dict(v))
        else:
            return Token("CALC", [Token("CODE", code), Token("dict", types.Dict(v))])

    def _help_expr_bin(self, items, op, Cls, post):
        i1 = items[0]
        i2 = items[1]

        if type(i1) == Tree and len(i1.data) > 5 and i1.data[0:5] == "EXPR_":
            return Tree("EXPR_"+post, [i1, i2])
        
        if type(i2) == Tree and len(i2.data) > 5 and i2.data[0:5] == "EXPR_":
            return Tree("EXPR_"+post, [i1, i2])

        if type(i1) == Tree and i1.data == "fun_call":
            return Tree("EXPR_"+post, [i1, i2])
            
        if type(i2) == Tree and i2.data == "fun_call":
            return Tree("EXPR_"+post, [i1, i2])
            
        # Evaluating const expr
        if (i1.type == "SIGNED_INT" or i1.type == "SIGNED_FLOAT") and (i2.type == "SIGNED_INT" 
                or i2.type == "SIGNED_FLOAT"):
            if(i1.type == "SIGNED_FLOAT" or i2.type == "SIGNED_FLOAT"):
                return Token("SIGNED_FLOAT", ir.Float(op(i1.value.value, i2.value.value)))
            else:
                return Token("SIGNED_INT", ir.Int(op(i1.value.value, i2.value.value)))
        # Generating code
        insts = []
        srcs = [0, 0]
        for i in range(0, 2):
            if items[i].type == "CODE":
                insts += items[i].value
                srcs[i] = items[i].value[-1].dst
            else:
                srcs[i] = items[i].value
        insts.append(Cls(srcs[0], srcs[1], self.uniq_var()))
        return Token("CODE", insts)

    def _help_expr_un(self, items, op, Cls, post):
        i1 = items[0]

        if type(i1) == Tree and len(i1.data) > 5 and i1.data[0:5] == "EXPR_":
            return Tree("EXPR_"+post, [i1])

        if type(i1) == Tree and i1.data == "fun_call":
            return Tree("EXPR_"+post, [i1])
            
        # Evaluating const expr
        if i1.type == "SIGNED_INT" or i1.type == "SIGNED_FLOAT":
            if i1.type == "SIGNED_FLOAT":
                return Token("SIGNED_FLOAT", ir.Float(op(i1.value.value)))
            else:
                return Token("SIGNED_INT", ir.Int(op(i1.value.value)))
        # Generating code
        insts = []
        srcs = None
        if items[0].type == "CODE":
            insts += items[0].value
            srcs = items[0].value[-1].dst
        else:
            srcs = items[0].value
        insts.append(Cls(srcs))
        return Token("CODE", insts)

    def _help_expr_log(self, items, op, Cls, post):
        i1 = items[0]
        i2 = items[1]

        if type(i1) == Tree and len(i1.data) > 5 and i1.data[0:5] == "EXPR_":
            return Tree("EXPR_"+post, [i1, i2])
        
        if type(i2) == Tree and len(i2.data) > 5 and i2.data[0:5] == "EXPR_":
            return Tree("EXPR_"+post, [i1, i2])

        if type(i1) == Tree and i1.data == "fun_call":
            return Tree("EXPR_"+post, [i1, i2])
            
        if type(i2) == Tree and i2.data == "fun_call":
            return Tree("EXPR_"+post, [i1, i2])

        if type(items[0].value) == ir.Bool and type(items[1].value) == ir.Bool:
            r = ir.Bool(op(items[0].value.value, items[1].value.value))
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

    def _help_expr_log_un(self, items, op, Cls, post):
        i1 = items[0]
        if type(i1) == Tree and len(i1.data) > 5 and i1.data[0:5] == "EXPR_":
            return Tree("EXPR_"+post, [i1])
        if type(i1) == Tree and i1.data == "fun_call":
            return Tree("EXPR_"+post, [i1])
        if type(items[0].value) == ir.Bool:
            r = ir.Bool(op(items[0].value.value))
            return Token(str(r), r)
        # Generating code
        insts = []
        src = None
        if items[0].type == "CODE":
            insts += items[0].value
            # Expr code
            src = items[0].value[-1].dst
        else:
            src = items[0].value
        insts.append(Cls(src, self.uniq_var()))
        return Token("CODE", insts)

    def expr_mul(self, items):
        return self._help_expr_bin(items, lambda a, b: a*b, ir.Mul, "MUL")

    def expr_add(self, items):
        return self._help_expr_bin(items, lambda a, b: a+b, ir.Add, "ADD")

    def expr_sub(self, items):
        return self._help_expr_bin(items, lambda a, b: a-b, ir.Sub, "SUB")

    def expr_fdiv(self, items):
        return self._help_expr_bin(items, lambda a, b: a / b, ir.FDiv, "FDIV")

    def expr_idiv(self, items):
        return self._help_expr_bin(items, lambda a, b: a // b, ir.IDiv, "IDIV")

    def expr_mod(self, items):
        return self._help_expr_bin(items, lambda a, b: a % b, ir.Mod, "MOD")

    def expr_exp(self, items):
        return self._help_expr_bin(items, lambda a, b: a ^ b, ir.Exp, "EXP")

    def expr_or(self, items):
        return self._help_expr_log(items, lambda a, b: a or b, ir.LOr, "OR")

    def expr_and(self, items):
        return self._help_expr_log(items, lambda a, b: a and b, ir.LAnd, "AND")

    def expr_lte(self, items):
        return self._help_expr_log(items, lambda a, b: a <= b, ir.Lte, "LTE")

    def expr_gte(self, items):
        return self._help_expr_log(items, lambda a, b: a >= b, ir.Gte, "GTE")

    def expr_gt(self, items):
        return self._help_expr_log(items, lambda a, b: a > b, ir.Gt, "GT")

    def expr_lt(self, items):
        return self._help_expr_log(items, lambda a, b: a < b, ir.Lt, "LT")

    def expr_eq(self, items):
        return self._help_expr_log(items, lambda a, b: a == b, ir.Eq, "EQ")

    def expr_neq(self, items):
        return self._help_expr_log(items, lambda a, b: a != b, ir.Neq, "NEQ")

    def expr_in(self, items):
        i1 = items[0]
        i2 = items[1]

        if type(i1) == Tree and len(i1.data) > 5 and i1.data[0:5] == "EXPR_":
            return Tree("EXPR_IN", [i1, i2])
        
        if type(i2) == Tree and len(i2.data) > 5 and i2.data[0:5] == "EXPR_":
            return Tree("EXPR_IN", [i1, i2])

        if type(i1) == Tree and i1.data == "fun_call":
            return Tree("EXPR_IN", [i1, i2])
            
        if type(i2) == Tree and i2.data == "fun_call":
            return Tree("EXPR_IN", [i1, i2])

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
        insts.append(ir.In(srcs[0], srcs[1], self.uniq_var()))
        return Token("CODE", insts)

    def expr_not(self, items):
        return self._help_expr_log_un(items, lambda a: not a, ir.LNot, "NOT")

    def expr_inc(self, items):
        return self._help_expr_un(items, lambda a: a + 1, ir.Inc, "INC")

    def expr_dec(self, items):
        return self._help_expr_un(items, lambda a: a - 1, ir.Dec, "DEC")
