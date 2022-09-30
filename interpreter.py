from symtable import SymbolTable
from lark import Lark, Transformer
from lark.lexer import Token
from lark.tree import Tree
from mash import Mash
import mash_exceptions as mex
from symbol_table import symb_table
import types
import ir
from sys import stderr

def debug(msg, opts):
    """
    Debug message
    """
    if opts.verbose:
        print("DEBUG: {}.".format(msg), file=stderr)

def info(msg, opts):
    """
    Info message
    """
    if opts.verbose:
        print(msg, file=stderr)

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

class Interpreter(Mash):
    """
    Mash interpreter
    """

    CONSTS = {"SIGNED_INT", "SIGNED_FLOAT", "Nil", "true", "false"}

    def __init__(self, opts, symb_table):
        self.opts = opts
        self.symb_table = symb_table
        self._last_id = 0

    def uniq_var(self):
        """
        Generates unique id
        """
        self._last_id += 1
        return f"@i_{self._last_id}"

    def generate_ir(self, root):
        """
        Generates internal IR from parse tree
        """
        debug(root, self.opts)
        # Declaration or print
        if type(root) == Token:
            # Variable declaration or print
            if root.type == "VAR_NAME":
                if not self.symb_table.exists_top(root.value):
                    self.symb_table.declare(root.value, ir.Nil())
                    return [ir.AssignVar(root.value, ir.Nil())]
                else:
                    r = self.uniq_var()
                    return [
                        ir.ToString(root.value, r),
                        ir.Print(r)
                    ]
            # Printing
            elif root.type == "scope_name":
                exists, msg = self.symb_table.exists(root.value)
                if exists:
                    r = self.uniq_var()
                    return [ir.Print(r)]
                else:
                    self.error(msg)
            # Generated code
            elif root.type == "CODE":
                return root.value+[ir.Print(root.value[-1].dst)]
        else:
            insts = []
            if root.data == "assignment":
                tree = root.children[1]
                if tree.type in Interpreter.CONSTS:
                    self.symb_table.assign(root.children[0].value, root.children[1].value)
                    return [ir.AssignVar(root.children[0].value, root.children[1].value)]
                elif tree.type == "CODE":
                    last_dst = tree.value[-1].dst
                    self.symb_table.assign(root.children[0].value, last_dst)
                    return tree.value+[ir.AssignVar(root.children[0].value, last_dst)]
                else:
                    raise mex.Unimplemented("UNIMPLEMENTED: Assignment not implemented for such value")
            # Block of code
            elif root.data == "code_block":
                for tree in root.children:
                    insts += self.generate_ir(tree)
            # If statement or elif part
            elif root.data == "if" or root.data == "elif":
                tree = root.children[0].children
                cnd = None
                tr = None
                fl = ir.Nop()
                # Condition check
                if tree[0].type == "CODE":
                    insts += tree[0].value
                    cnd = insts[-1].dst
                else:
                    s, m = self.symb_table.exists(tree[0].value)
                    if not s:
                        self.error(m)
                    cnd = tree[0].value
                # True branch
                # TODO: Push a new symbtable
                tr = self.generate_ir(tree[1])
                if root.data == "elif" and len(root.children) > 1:
                    fl = self.generate_ir(Tree("elif", root.children[1:]))
                # False branch
                elif len(tree) > 2:
                    if tree[2].data == "else":
                        fl = self.generate_ir(tree[2].children[0])
                    elif tree[2].data == "elif":
                        fl = self.generate_ir(Tree("elif", tree[2:]))
                insts.append(ir.If(cnd, tr, fl))
            # While loop
            elif root.data == "while":
                tree = tree = root.children[0].children
                cnd = None
                # Condition check
                if tree[0].type == "CODE":
                    insts += tree[0].value
                    cnd = insts[-1].dst
                elif tree[0].type == "VAR_NAME" or tree[0].type == "scope_name":
                    s, m = self.symb_table.exists(tree[0].value)
                    if not s:
                        # TODO: Change to an exception 
                        self.error(m)
                    cnd = tree[0].value
                else:
                    cnd = tree[0].value
                insts.append(ir.While(cnd, self.generate_ir(tree[1])))
            return insts
        debug("No instructions generated for: {}".format(root), self.opts)
        return []

    def interpret_top_level(self, root):
        """
        Interprets top level tree
        """
        self.ir = []
        # declaration or print
        for i in root.children:
            # i.data, i.children
            self.ir += self.generate_ir(i)
        if self.opts.verbose:
            debug("Generated code:", self.opts)
            for i in self.ir:
                info(i, self.opts)
        return self.ir

    def interpret(self, code):
        """
        Interprets passed in ir
        @param code IR code to be interpreted
        """
        self.symb_table.clear_all()
        self.symb_table.analyzer = False
        for i in code:
            i.exec()


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

    def Nil(self, items):
        return Token("Nil", ir.Nil())

    def true(self, items):
        return Token("true", ir.Bool(True))

    def false(self, items):
        return Token("false", ir.Bool(False))

    def _help_expr_bin(self, items, op, Cls):
        srcs = [0, 0]
        # Evaluating const expr
        if (items[0].type == "SIGNED_INT" or items[0].type == "SIGNED_FLOAT") and (items[1].type == "SIGNED_INT" 
                or items[1].type == "SIGNED_FLOAT"):
            if(items[0].type == "SIGNED_FLOAT" or items[1].type == "SIGNED_FLOAT"):
                return Token("SIGNED_FLOAT", ir.Float(op(items[0].value.value, items[1].value.value)))
            else:
                return Token("SIGNED_INT", ir.Int(op(items[0].value.value, items[1].value.value)))
        # Generating code
        insts = []
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

    def expr_mul(self, items):
        return self._help_expr_bin(items, lambda a, b: a*b, ir.Mul)

    def expr_add(self, items):
        return self._help_expr_bin(items, lambda a, b: a+b, ir.Add)

    def expr_sub(self, items):
        return self._help_expr_bin(items, lambda a, b: a-b, ir.Sub)
        

def interpret(opts, code):
    """
    Interpret mash code
    """
    debug("Parser started", opts)
    parser = Parser(code, opts)
    tree = parser.parse()
    debug("Parser finished", opts)
    if opts.parse_only:
        return
    interpreter = Interpreter(opts, symb_table)
    ir_code = interpreter.interpret_top_level(ConstTransformer(symb_table).transform(tree))
    debug("IR generation done", opts)
    if opts.code_only:
        for i in ir_code:
            print(i)
        return
    debug("Running IR", opts)
    interpreter.interpret(ir_code)
    debug("Finished running IR", opts)
    
