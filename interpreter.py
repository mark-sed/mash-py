from lark import Lark, Transformer
from lark.lexer import Token
import ir
import sys
from mash import Mash

def debug(msg, opts):
    """
    Debug message
    """
    if opts.verbose:
        print("DEBUG: {}.".format(msg))

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
            print(parse_tree.pretty())
        return parse_tree

class Symbol:

    def key(self):
        return "!!!ERROR"

class Var(Symbol):
    """
    Variable
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def key(self):
        return self.name

    def __str__(self):
        return f"{self.name} = {self.value}"

class Fun(Symbol):
    """
    Function
    """
    ...

class SymbTable(Mash):
    """
    Symbolic table
    """
    GLOB_TBL = {
        #"print?1": {ir.Print("@0")}
    }

    def __init__(self):
        self.tbls = []
        self.tbls.append(SymbTable.GLOB_TBL)

    def declare(self, symb):
        """
        Declares variable for the first time.
        If it already exists an error is raised.
        """
        if self.exists_top(symb.key()):
            self.error(f"Redefinition of {symb.key()}")
        self.tbls[-1][symb.key()] = symb

    def exists_top(self, symb):
        return symb in self.tbls[-1]

    def exists(self, symb):
        nested = False
        s = symb
        if type(symb) == list:
            s = symb[0]
            nested = True

        for t in reversed(self.tbls):
            if s in t:
                if not nested:
                    return (True, "")
                else:
                    # TODO: Add when classes and spaces added
                    print("NOT IMPLEMENTED!!")
        return (False, f"Undefined reference to '{s}'")

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
        # Declaration or print
        print(root)
        if type(root) == Token:
            # Variable declaration or print
            if root.type == "VAR_NAME":
                if not self.symb_table.exists_top(root.value):
                    v = Var(root.value, None)
                    self.symb_table.declare(v)
                    return [ir.AssignVar(v.key(), ir.NIL())]
                else:
                    r = self.uniq_var()
                    return [
                        ir.ToString(r, root.value),
                        ir.Print(r)
                    ]
            # Printing
            elif root.type == "scope_name":
                exists, msg = self.symb_table.exists(root.value)
                if exists:
                    r = self.uniq_var()
                    return [
                        ir.ToString(r, root.value),
                        ir.Print(r)
                    ]
                else:
                    self.error(msg)
        else:
            # If statement
            if root.data == "if":
                tr = root.children[0].children
                print(tr[0])

        
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
        print("Generated code:")
        for i in self.ir:
            print(i)



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
        items[0].value = int(items[0].value)
        return items

    def float(self, items):
        items[0].value = float(items[0].value)
        return items

    def expr_mul(self, items):
        srcs = [items[0].value, items[1].value]
        # Evaluating const expr
        if (items[0].type == "SIGNED_INT" or items[0].type == "SIGNED_FLOAT") and (items[1].type == "SIGNED_INT" 
                or items[1].type == "SIGNED_FLOAT"):
            if(items[0].type == "SIGNED_FLOAT" or items[1].type == "SIGNED_FLOAT"):
                return Token("SIGNED_FLOAT", items[0]*items[1])
            else:
                return Token("SIGNED_INT", items[0]*items[1])
        # Generating code

        ##### FIX ALL! Calc constants and generate code for others, but watch out for function calls and such


        for i in range(0, 1):
            if items[i].type == "CODE":
                # Expr code
                if issubclass(items[i].value[-1], ir.Expr):
                    srcs[i] = items[i].value[0].dst
        return Token("CODE", [ir.Mul(self.uniq_var(), *srcs)])




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
    symb_table = SymbTable()
    interpreter = Interpreter(opts, symb_table)
    interpreter.interpret_top_level(ConstTransformer(symb_table).transform(tree))
    
