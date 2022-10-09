from lark.lexer import Token
from lark.tree import Tree
from sys import stderr
from mash import Mash
import mash_exceptions as mex
from symbol_table import symb_table, SymbTable
import ir
import parsing
import mash_types as types
from parsing import Parser
from debugging import info, debug

class Interpreter(Mash):
    """
    Mash interpreter
    """

    CONSTS = {"SIGNED_INT", "SIGNED_FLOAT", "nil", "true", "false", "string", "list"}

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

    def generate_ir(self, root, silent=False):
        """
        Generates internal IR from parse tree
        """
        debug(root, self.opts)
        # Declaration or print
        if type(root) == Token:
            # Variable declaration or print
            if root.type == "VAR_NAME":
                if not self.symb_table.exists(root.value):
                    self.symb_table.declare(root.value, ir.Nil())
                    return [ir.AssignVar(root.value, ir.Nil())]
                else:
                    if not silent:
                        return [ir.Print(root.value)]
            # Printing
            elif root.type == "scope_name":
                exists, msg = self.symb_table.exists(root.value)
                if exists:
                    if not silent:
                        return [ir.Print(root.value)]
                else:
                    self.error(msg)
            # Generated code
            elif root.type == "CODE":
                if not silent:
                    return root.value+[ir.Print(root.value[-1].dst)]
                else:
                    return root.value
            # Const print
            elif root.type in Interpreter.CONSTS:
                if not silent:
                    return [ir.Print(root.value)]
            elif root.value == "break":
                return [ir.Break()]
            elif root.value == "continue":
                return [ir.Continue()]
        else:
            insts = []
            if root.data == "assignment":
                tree = root.children[1]
                if type(tree) == Token:
                    if tree.type in Interpreter.CONSTS:
                        self.symb_table.assign(root.children[0].value, root.children[1].value)
                        return [ir.AssignVar(root.children[0].value, root.children[1].value)]
                    elif tree.type == "CODE":
                        last_dst = tree.value[-1].dst
                        self.symb_table.assign(root.children[0].value, last_dst)
                        return tree.value+[ir.AssignVar(root.children[0].value, last_dst)]
                    elif tree.type == "CALC":
                        subtree = tree.value
                        for i in subtree:
                            if i.type == "CODE":
                                insts += i.value
                            else:
                                if i.type in Interpreter.CONSTS:
                                    self.symb_table.assign(root.children[0].value, i.value)
                                    insts += [ir.AssignVar(root.children[0].value, i.value)]
                    else:
                        raise mex.Unimplemented("Assignment not implemented for such value")
                else:
                    if tree.data == "fun_call":
                        return self.generate_ir(tree, True)+[ir.AssignVar(root.children[0].value, SymbTable.RETURN_NAME)]
                    elif root.data == "assignment":
                        assign = self.generate_ir(tree)
                        return assign+[ir.AssignVar(root.children[0].value, assign[-1].dst)]
                    else:
                        raise mex.Unimplemented("Assignment not implemented for such value")
            # Block of code
            elif root.data == "code_block":
                symb_table.push()
                for tree in root.children:
                    insts += self.generate_ir(tree)
                symb_table.pop()
            # Block of function code
            elif root.data == "fun_code_block":
                for tree in root.children:
                    insts += self.generate_ir(tree)
            # Function call
            elif root.data == "fun_call":
                tree = root.children
                name = tree[0].value
                args = tree[1].value
                insts.append(ir.FunCall(name, args))
                if not silent:
                    insts.append(ir.Print(SymbTable.RETURN_NAME))
            # If statement or elif part
            elif root.data == "if" or root.data == "elif":
                tree = root.children[0].children
                cnd = None
                tr = None
                fl = ir.Nop()
                # Condition check
                if type(tree[0]) == Token and tree[0].type == "CODE":
                    insts += tree[0].value
                    cnd = insts[-1].dst
                else:
                    s, m = self.symb_table.exists(tree[0].value)
                    if not s:
                        self.error(m)
                    cnd = tree[0].value
                # True branch
                if type(tree[1]) == Tree and tree[1].data != "code_block":
                    symb_table.push()
                tr = self.generate_ir(tree[1])
                if type(tree[1]) == Tree and tree[1].data != "code_block":
                    symb_table.pop()
                
                if root.data == "elif" and len(root.children) > 1:
                    fl = self.generate_ir(Tree("elif", root.children[1:]))
                # False branch
                elif len(tree) > 2:
                    if tree[2].data == "else":
                        if type(tree[2].children[0]) == Token and tree[2].children[0].type != "code_block" or tree[2].children[0].data != "code_block":
                            symb_table.push()
                        fl = self.generate_ir(tree[2].children[0])
                        if type(tree[2].children[0]) == Token and tree[2].children[0].type != "code_block" or tree[2].children[0].data != "code_block":
                            symb_table.pop()
                    elif tree[2].data == "elif":
                        fl = self.generate_ir(Tree("elif", tree[2:]))
                insts.append(ir.If(cnd, tr, fl))
            # While loop
            elif root.data == "while":
                tree = root.children[0].children
                cnd = None
                # Condition check
                if type(tree[0]) == Token and tree[0].type == "CODE":
                    insts += tree[0].value
                    cnd = insts[-1].dst
                elif (type(tree[0]) == Token and tree[0].type == "VAR_NAME") or (type(tree[0]) == Token and tree[0].type == "scope_name"):
                    s, m = self.symb_table.exists(tree[0].value)
                    if not s:
                        # TODO: Change to an exception 
                        raise mex.UndefinedReference(m)
                    cnd = tree[0].value
                else:
                    cnd = tree[0].value
                if type(tree[1]) == Tree and tree[1].data != "code_block":
                    symb_table.push()
                t = self.generate_ir(tree[1])
                if type(tree[1]) == Tree and tree[1].data != "code_block":
                    symb_table.pop()
                insts.append(ir.While(cnd, t))
            # Do while loop
            elif root.data == "do_while":
                tree = root.children[0].children
                if type(tree[0]) == Tree and tree[0].data != "code_block":
                    symb_table.push()
                t = self.generate_ir(tree[0])
                if type(tree[0]) == Tree and tree[0].data != "code_block":
                    symb_table.pop()
                cnd = None
                # Condition check
                if type(tree[1]) == Token and tree[1].type == "CODE":
                    insts += tree[1].value
                    cnd = insts[-1].dst
                elif (type(tree[1]) == Token and tree[1].type == "VAR_NAME") or (type(tree[1]) == Token and tree[1].type == "scope_name"):
                    s, m = self.symb_table.exists(tree[1].value)
                    if not s:
                        raise mex.UndefinedReference(m)
                    cnd = tree[1].value
                else:
                    cnd = tree[1].value
                insts.append(ir.DoWhile(t, cnd))
            # For loop
            elif root.data == "for":
                tree = root.children[0].children
                i = tree[0].value
                symb_table.assign(i, types.Nil())
                l = tree[1].value
                if type(tree[2]) == Tree and tree[2].data != "code_block":
                    symb_table.push()
                t = self.generate_ir(tree[2])
                if type(tree[2]) == Tree and tree[2].data != "code_block":
                    symb_table.pop()
                insts.append(ir.For(i, l, t))
            # Function
            elif root.data == "function":
                tree = root.children
                name = tree[0].value
                args = tree[1].value
                # fun_code_block does not push the frame itself
                symb_table.push()
                # Push args
                for k, v in args:
                    symb_table.declare(k, v)
                body = self.generate_ir(tree[2])
                symb_table.pop()
                insts.append(ir.Fun(name, args, body))
            elif root.data == "return":
                if len(root.children) == 0:
                    value = types.Nil()
                else:
                    value = root.children[0].value
                insts.append(ir.Return(value))
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
    ir_code = interpreter.interpret_top_level(parsing.ConstTransformer(symb_table).transform(tree))
    debug("IR generation done", opts)
    if opts.code_only:
        for i in ir_code:
            print(i)
        return
    debug("Running IR", opts)
    interpreter.interpret(ir_code)
    debug("Finished running IR", opts)
    
