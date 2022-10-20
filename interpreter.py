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

    CONSTS = {"SIGNED_INT", "SIGNED_FLOAT", "nil", "true", "false", "string", "list", "dict"}

    def __init__(self, opts, symb_table):
        self.opts = opts
        self.symb_table = symb_table
        self._last_id = 0

    def uniq_var(self):
        """
        Generates unique id
        """
        self._last_id += 1
        return f"$i_{self._last_id}"

    def generate_subexpr(self, src):
        """
        Subexpression code generation and evaluation
        """
        insts = []
        dst = None
        if type(src) == Token:
            if src.type in Interpreter.CONSTS or type(src.value) == str:
                dst = src.value
            elif src.type == "CODE":
                insts += src.value
                dst = insts[-1].dst
            else:
                raise mex.Unimplemented("Subexpression")
        else:
            if src.data == "fun_call":
                insts += self.multi_call(src)
                dst = self.uniq_var()
                insts.append(ir.AssignVar(dst, SymbTable.RETURN_NAME))
            elif src.data == "member":
                s, extra_insts = self.generate_subexpr(src.children[0])
                insts += extra_insts
                index, extra_insts = self.generate_subexpr(src.children[1])
                insts += extra_insts
                dst = self.uniq_var()
                insts.append(ir.Member(s, index, dst))
            elif len(src.data) > 5 and src.data[0:5] == "EXPR_":
                dst, insts = self.generate_expr(src)
            else:
                raise mex.Unimplemented("Subexpression")
        return (dst, insts)

    def generate_cond(self, tree):
        """
        Generates code for conditions (for if, while and do while)
        """
        insts = []
        cnd = None
        if type(tree[0]) == Token and tree[0].type == "CODE":
            insts += tree[0].value
            cnd = insts[-1].dst
        else:
            if type(tree[0]) == Tree:
                rval, gen = self.generate_expr(tree[0])
                insts += gen
                cnd = rval
            else:
                if tree[0].type in Interpreter.CONSTS:
                    cnd = tree[0].value
                else:
                    s, m = self.symb_table.exists(tree[0].value)
                    if not s:
                        raise mex.UndefinedReference(m)
                    cnd = tree[0].value
        return (cnd, insts)

    def generate_expr(self, root):
        """
        Genrates instructions for expressions
        @return List of instructions and variable or value containing the result
        """
        if type(root) == Token:
            return (root.value, [])
        else:
            if root.data == "EXPR_NOT" or root.data == "EXPR_INC" or root.data == "EXPR_DEC":
                lr, left = self.generate_expr(root.children[0])
                iname = root.data[5:]
                opres = self.uniq_var()
                symb_table.assign(opres, None)
                if iname == "NOT":
                    return (opres, left+[ir.LNot(lr, opres)])
                elif iname == "DEC":
                    return (opres, left+[ir.Dec(lr, opres)])
                elif iname == "INC":
                    return (opres, left+[ir.Inc(lr, opres)])
                else:
                    raise mex.Unimplemented(root.data)
            elif root.data == "EXPR_TIF":
                lr, left = self.generate_expr(root.children[0])
                mr, mid = self.generate_expr(root.children[1])
                rr, right = self.generate_expr(root.children[2])
                opres = self.uniq_var()
                symb_table.assign(opres, None)
                return (opres, left+mid+right+[ir.TernaryIf(lr, mr, rr, opres)])
            elif len(root.data) > 5 and root.data[0:5] == "EXPR_":
                lr, left = self.generate_expr(root.children[0])
                rr, right = self.generate_expr(root.children[1])
                iname = root.data[5:]
                opres = self.uniq_var()
                symb_table.assign(opres, None)
                if iname == "ADD":
                    return (opres, left+right+[ir.Add(lr, rr, opres)])
                elif iname == "MUL":
                    return (opres, left+right+[ir.Mul(lr, rr, opres)])
                elif iname == "SUB":
                    return (opres, left+right+[ir.Sub(lr, rr, opres)])
                elif iname == "FDIV":
                    return (opres, left+right+[ir.FDiv(lr, rr, opres)])
                elif iname == "IDIV":
                    return (opres, left+right+[ir.IDiv(lr, rr, opres)])
                elif iname == "MOD":
                    return (opres, left+right+[ir.Mod(lr, rr, opres)])
                elif iname == "EXP":
                    return (opres, left+right+[ir.Exp(lr, rr, opres)])
                elif iname == "OR":
                    return (opres, left+right+[ir.LOr(lr, rr, opres)])
                elif iname == "AND":
                    return (opres, left+right+[ir.LAnd(lr, rr, opres)])
                elif iname == "LTE":
                    return (opres, left+right+[ir.Lte(lr, rr, opres)])
                elif iname == "GTE":
                    return (opres, left+right+[ir.Gte(lr, rr, opres)])
                elif iname == "GT":
                    return (opres, left+right+[ir.Gt(lr, rr, opres)])
                elif iname == "LT":
                    return (opres, left+right+[ir.Lt(lr, rr, opres)])
                elif iname == "EQ":
                    return (opres, left+right+[ir.Eq(lr, rr, opres)])
                elif iname == "NEQ":
                    return (opres, left+right+[ir.Neq(lr, rr, opres)])
                elif iname == "IN":
                    return (opres, left+right+[ir.In(lr, rr, opres)])
                else:
                    raise mex.Unimplemented("Runtime expression '"+iname+"'")
            elif root.data == "fun_call":
                opres = self.uniq_var()
                symb_table.assign(SymbTable.RETURN_NAME, None)
                symb_table.assign(opres, SymbTable.RETURN_NAME)
                return (opres, self.generate_ir(root, True)+[ir.AssignVar(opres, SymbTable.RETURN_NAME)])
                
    def op_assign(self, dst, value, op):
        """
        Returns correct operation or assignment based on used operator
        E.g.: a = 4 vs a += 4
        """
        if op == "=":
            self.symb_table.assign(dst, value)
            return ir.AssignVar(dst, value)
        elif op == "+=":
            return ir.Add(dst, value, dst)
        elif op == "-=":
            return ir.Sub(dst, value, dst)
        elif op == "*=":
            return ir.Mul(dst, value, dst)
        elif op == "/=":
            return ir.FDiv(dst, value, dst)
        elif op == "//=":
            return ir.IDiv(dst, value, dst)
        elif op == "%=":
            return ir.Mod(dst, value, dst)
        elif op == "^=":
            return ir.Exp(dst, value, dst)
        else:
            raise mex.Unimplemented("Assignment operator "+str(op))

    def generate_fun(self, root):
        insts = []
        tree = root.children
        name = tree[0].value
        args = tree[1].value
        for i, a in enumerate(args):
            if type(a) == list:
                # Expression in positional argument
                insts += a
                args[i] = insts[-1].dst
            elif type(a) == tuple and type(a[1]) == list:
                # Expression in named argument
                insts += a[1]
                args[i] = (a[0], insts[-1].dst)
            elif type(a) == Tree and a.data == "fun_call":
                # Function call
                insts += self.generate_ir(a, True)
                retv = self.uniq_var()
                symb_table.assign(retv, SymbTable.RETURN_NAME)
                insts.append(ir.AssignVar(retv, SymbTable.RETURN_NAME))
                args[i] = retv
            elif type(a) == Tree and len(a.data) > 5 and a.data[:5] == "EXPR_":
                # Expression nor parsable in the transformer
                retv, insts = self.generate_expr(a)
                symb_table.assign(retv, None)
                args[i] = retv
            elif type(a) == tuple and type(a[1]) == Tree and a[1].data == "fun_call":
                # Function call to named arg
                insts += self.generate_ir(a[1], True)
                retv = self.uniq_var()
                symb_table.assign(retv, SymbTable.RETURN_NAME)
                insts.append(ir.AssignVar(retv, SymbTable.RETURN_NAME))
                args[i] = (a[0], retv)
            elif type(a) == tuple and type(a[1]) == Tree and len(a[1].data) > 5 and a[1].data[:5] == "EXPR_":
                # Expression nor parsable in the transformer (for named arg)
                retv, insts = self.generate_expr(a[1])
                symb_table.assign(retv, None)
                args[i] = (a[0], retv)
        insts.append(ir.FunCall(name, args))
        return insts

    def multi_call(self, root):
        if type(root.children[0]) == Tree and root.children[0].data == "fun_call":
            v = root.children[0]
            # Function call over returned value
            return self.multi_call(v)+[ir.FunCall(SymbTable.RETURN_NAME, root.children[1].value)]
        elif type(root.children[0]) == Tree and root.children[0].data == "member":
            v = root.children[0]
            ret, inst = self.generate_subexpr(v)
            # Function call over member
            return inst+[ir.FunCall(ret, root.children[1].value)]
        else:
            return self.generate_fun(root)

    def generate_ir(self, root, silent=False):
        """
        Generates internal IR from parse tree
        """
        debug(root, self.opts)
        # Declaration or print
        if type(root) == Token:
            # Variable declaration or print
            if root.type == "VAR_NAME":
                self.symb_table.assign(root.value, ir.Nil())
                if not silent:
                    insts = [ir.SetOrPrint(root.value, ir.Nil())]
                else:
                    insts += [ir.SetIfNotSet(root.value, ir.Nil())]
                return insts
            # Printing
            elif root.type == "scope_name":
                exists, msg = self.symb_table.exists(root.value)
                if exists:
                    if not silent:
                        return [ir.Print(root.value)]
                else:
                    raise mex.UndefinedReference(msg)
            # Generated calculation
            elif root.type == "CALC":
                insts = []
                subtree = root.value
                for i in subtree:
                    if i.type == "CODE":
                        insts += i.value
                    else:
                        if i.type in Interpreter.CONSTS:
                            if not silent:
                                insts.append(ir.Print(i.value))
                return insts
            # Generated code
            elif root.type == "CODE":
                insts = []
                for i in root.value:
                    if type(i) == Tree or type(i) == Token:
                        insts += self.generate_ir(i, silent)
                    else:
                        insts.append(i)
                if not silent:
                    insts.append(ir.Print(root.value[-1].dst))
                return insts
            # Const print
            elif root.type in Interpreter.CONSTS:
                if not silent:
                    return [ir.Print(root.value)]
            # Break
            elif root.value == "break":
                return [ir.Break()]
            # Continue
            elif root.value == "continue":
                return [ir.Continue()]
            # internal
            elif root.value == "internal":
                return [ir.Internal()]
        else:
            insts = []
            if root.data == "assignment" or root.data == "op_assign":
                tree = root.children[1]
                op = "="
                if root.data == "op_assign":
                    tree = root.children[2]
                    op = root.children[1].value
                if type(tree) == Token:
                    if tree.type in Interpreter.CONSTS:
                        insts.append(self.op_assign(root.children[0].value, tree.value, op))
                    elif tree.type == "CODE":
                        last_dst = tree.value[-1].dst
                        insts += tree.value+[self.op_assign(root.children[0].value, last_dst, op)]
                    elif tree.type == "CALC":
                        subtree = tree.value
                        for i in subtree:
                            if i.type == "CODE":
                                insts += i.value
                            else:
                                if i.type in Interpreter.CONSTS:
                                    insts.append(self.op_assign(root.children[0].value, i.value, op))
                    elif tree.type == "VAR_NAME":
                        insts.append(self.op_assign(root.children[0].value, tree.value, op))
                    else:
                        raise mex.Unimplemented("Assignment not implemented for such value")
                else:
                    if tree.data == "fun_call":
                        return self.generate_ir(tree, True)+[self.op_assign(root.children[0].value, SymbTable.RETURN_NAME, op)]
                    elif tree.data == "assignment":
                        if root.data == "op_assign":
                            raise mex.SyntaxError("Assignment cannot be chained with compound assignment")
                        assign = self.generate_ir(tree, True)
                        self.symb_table.assign(root.children[0].value, assign[-1].dst)
                        insts += assign+[ir.AssignVar(root.children[0].value, assign[-1].dst)]
                    elif tree.data == "member":
                        insts += self.generate_ir(tree, True)
                        insts.append(self.op_assign(root.children[0].value, insts[-1].dst, op))
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
            # Space
            elif root.data == "space":
                symb_table.push_space(root.children[0].value)
                insts.append(ir.SpacePush(root.children[0].value))
                for tree in root.children[1:]:
                    insts += self.generate_ir(tree)
                insts.append(ir.SpacePop())
                symb_table.pop_space()
            # Function call
            elif root.data == "fun_call":
                insts += self.multi_call(root)
                if not silent:
                    insts.append(ir.Print(SymbTable.RETURN_NAME))
            # If statement or elif part
            elif root.data == "if" or root.data == "elif":
                tree = root.children[0].children
                cnd, insts = self.generate_cond(tree)
                tr = None
                fl = ir.Nop()
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
                cnd, insts = self.generate_cond(tree)
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
                l = None
                # list might be complex
                if type(tree[1]) == Token and tree[1].type == "CODE":
                        insts += tree[1].value
                        l = insts[-1].dst
                elif type(tree[1]) == Tree:
                    if tree[1].data == "fun_call":
                        insts += self.multi_call(tree[1])
                        l = SymbTable.RETURN_NAME
                    elif len(tree[1].data) > 5 and tree[1].data[0:5] == "EXPR_":
                        l, extra = self.generate_expr(tree[1])
                        insts += extra
                    else:
                        raise mex.Unimplemented("Such expression in for loop")
                elif (type(tree[1]) == Token and tree[1].type == "VAR_NAME") or (type(tree[1]) == Token and tree[1].type == "scope_name"):
                    s, m = self.symb_table.exists(tree[1].value)
                    if not s:
                        raise mex.UndefinedReference(m)
                    l = tree[1].value
                else:
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
            # Return
            elif root.data == "return":
                if len(root.children) == 0:
                    value = types.Nil()
                else:
                    if type(root.children[0]) == Tree:
                        value, insts = self.generate_expr(root.children[0])
                    elif root.children[0].type == "CODE":
                        insts += root.children[0].value
                        value = insts[-1].dst
                    elif root.children[0].type == "CALC":
                        for i in root.children[0].value:
                            if type(i) == Token or type(i) == Tree:
                                insts += self.generate_ir(i, True)
                        value = insts[-1].dst
                    else:
                        value = root.children[0].value
                    insts.append(ir.Return(value))
            # Silent expr
            elif root.data == "silent_expr":
                insts += self.generate_ir(root.children[0], True)
            # Expression that could not be constructed at parse time
            elif len(root.data) > 5 and root.data[0:5] == "EXPR_":
                resvar, insts = self.generate_expr(root)
                if not silent:
                    return insts+[ir.Print(resvar)]
            # Member []
            elif root.data == "member":
                src, extra_insts = self.generate_subexpr(root.children[0])
                insts += extra_insts
                index, extra_insts = self.generate_subexpr(root.children[1])
                insts += extra_insts
                dst = self.uniq_var()
                insts.append(ir.Member(src, index, dst))
                if not silent:
                    insts.append(ir.Print(dst))
            # Subrange
            elif root.data == "slice":
                src, extra_insts = self.generate_subexpr(root.children[0])
                insts += extra_insts
                indices = []
                a = 1
                was_value = False
                while a < len(root.children):
                    i = root.children[a]
                    if type(i) == Tree or (type(i) == Token and i.type != "MEM_SEP"):
                        index, extra_insts = self.generate_subexpr(i)
                        insts += extra_insts
                        indices.append(index)
                        was_value = True
                    elif not was_value:
                        indices.append(None)
                    a += 1
                dst = self.uniq_var()
                # Pad missing
                indices += [None] * (3 - len(indices))
                insts.append(ir.Slice(src, *indices, dst))
                if not silent:
                    insts.append(ir.Print(dst))
            return insts
        debug("No instructions generated for: {}".format(root), self.opts)
        return []

    def interpret_top_level(self, root):
        """
        Interprets top level tree
        """
        self.symb_table.analyzer = True
        self.ir = []
        # declaration or print
        for i in root.children:
            # i.data, i.children
            self.ir += self.generate_ir(i)
        # Parsing nodes passed down from the parser into instructions
        for c, i in enumerate(self.ir):
            if type(i) == Tree or type(i) == Token:
                gen = self.generate_ir(i, True)
                self.ir[c:c+1] = gen
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
        self.symb_table.analyzer = False
        for i in code:
            i.exec()
        #print("\n\n"+str(symb_table))

def interpret(opts, code, libmash_code):
    """
    Interpret mash code
    """
    debug("Parser started", opts)
    parser = Parser(code, opts)
    tree = parser.parse()
    debug("Parser finished", opts)
    if opts.parse_only:
        return

    if not opts.no_libmash:
        debug("Parsing of libmash started", opts)
        parser = Parser(libmash_code, opts)
        libmash_tree = parser.parse()
        debug("Parsing of libmash finished", opts)

    debug("Code generation started", opts)
    interpreter = Interpreter(opts, symb_table)
    if not opts.no_libmash:
        lib_code = interpreter.interpret_top_level(parsing.ConstTransformer(symb_table).transform(libmash_tree))
    debug("Libmash code generated", opts)
    ir_code = interpreter.interpret_top_level(parsing.ConstTransformer(symb_table).transform(tree))
    debug("IR generation done", opts)
    if opts.code_only:
        for i in ir_code:
            print(i)
        return
    debug("Running IR", opts)
    symb_table.clear_all()
    if not opts.no_libmash:
        interpreter.interpret(lib_code)
    interpreter.interpret(ir_code)
    debug("Finished running IR", opts)
    
