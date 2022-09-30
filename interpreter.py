from lark import Lark, Transformer
from lark.lexer import Token
from lark.tree import Tree
from mash import Mash
import mash_exceptions as mex
from symbol_table import symb_table
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
                    self.symb_table.declare(root.value, ir.NIL())
                    return [ir.AssignVar(root.value, ir.NIL())]
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
                if root.children[1].type in {"SIGNED_INT", "SIGNED_FLOAT", "nil", "true", "false"}:
                    self.symb_table.assign(root.children[0].value, root.children[1].value)
                    return [ir.AssignVar(root.children[0].value, root.children[1].value)]
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
        return Token("SIGNED_INT", int(items[0].value))

    def float(self, items):
        return Token("SIGNED_FLOAT", float(items[0].value))

    def nil(self, items):
        return Token("nil", None)

    def true(self, items):
        return Token("true", True)

    def false(self, items):
        return Token("false", False)

    def expr_mul(self, items):
        srcs = [0, 0]
        # Evaluating const expr
        if (items[0].type == "SIGNED_INT" or items[0].type == "SIGNED_FLOAT") and (items[1].type == "SIGNED_INT" 
                or items[1].type == "SIGNED_FLOAT"):
            if(items[0].type == "SIGNED_FLOAT" or items[1].type == "SIGNED_FLOAT"):
                return Token("SIGNED_FLOAT", items[0].value*items[1].value)
            else:
                return Token("SIGNED_INT", items[0].value*items[1].value)
        # Generating code
        insts = []
        for i in range(0, 2):
            if items[i].type == "CODE":
                insts += items[i].value
                # Expr code
                #if issubclass(type(items[i].value[-1]), ir.Expr):
                srcs[i] = items[i].value[0].dst
            else:
                srcs[i] = items[i].value
        insts.append(ir.Mul(srcs[0], srcs[1], self.uniq_var()))
        return Token("CODE", insts)

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
    debug("Running IR", opts)
    interpreter.interpret(ir_code)
    debug("Finished running IR", opts)
    
