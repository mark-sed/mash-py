from mash_parser import Token, Tree
from sys import stderr
from mash import Mash
import mash_exceptions as mex
from symbol_table import symb_table, SymbTable
import ir
import parsing
import mash_types as types
from parsing import Parser
from debugging import info, debug
from pathlib import Path

class Interpreter(Mash):
    """
    Mash interpreter
    """

    CONSTS = {"SIGNED_INT", "SIGNED_FLOAT", "nil", "true", "false", "string", "list", "dict"}

    def __init__(self, opts, symb_table):
        self.opts = opts
        self.symb_table = symb_table
        self._last_id = 0
        self._last_lambda = 0
        self._last_space = 0
        self.last_inst = None
        self.code_blocks = None
        self.main = False
        # Parse output notebook format if set
        self.output_file = self.opts.output
        if self.output_file is not None:
            self.output_format = self.output_file[self.output_file.rfind('.')+1:]
        else:
            self.output_format = None
        self.output_notes = self.opts.output_notes

    def uniq_var(self):
        """
        Generates unique id
        """
        self._last_id += 1
        return f"'i_{self._last_id}"

    def uniq_lambda(self):
        self._last_lambda += 1
        return f"λ{self._last_lambda}"

    def uniq_space(self):
        self._last_space += 1
        return f"AnonymousSpace{self._last_space}"

    def generate_subexpr(self, src):
        """
        Subexpression code generation and evaluation
        """
        insts = []
        dst = None
        if type(src) == Token:
            if src.type in Interpreter.CONSTS or type(src.value) == str or type(src.value) == list:
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
            elif src.data == "member" or src.data == "range":
                insts = self.generate_ir(src, True)
                dst = insts[-1].dst
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
        if type(tree) == Token and tree.type == "CODE":
            insts += tree.value
            cnd = insts[-1].dst
        else:
            if type(tree) == Tree:
                rval, gen = self.generate_expr(tree)
                insts += gen
                cnd = rval
            else:
                if tree.type in Interpreter.CONSTS:
                    cnd = tree.value
                else:
                    s, m = self.symb_table.exists(tree.value)
                    if not s:
                        raise mex.UndefinedReference(m)
                    cnd = tree.value
        return (cnd, insts)

    def generate_expr(self, root):
        """
        Genrates instructions for expressions
        @return List of instructions and variable or value containing the result
        """
        if type(root) == Token:
            return (root.value, [])
        else:
            if root.data == "EXPR_NOT":
                lr, left = self.generate_expr(root.children[0])
                iname = root.data[5:]
                opres = self.uniq_var()
                symb_table.assign(opres, None)
                return (opres, left+[ir.LNot(lr, opres)])
            if root.data == "EXPR_NEG":
                lr, left = self.generate_expr(root.children[0])
                iname = root.data[5:]
                opres = self.uniq_var()
                symb_table.assign(opres, None)
                return (opres, left+[ir.Neg(lr, opres)])
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
                if iname == "CAT":
                    return (opres, left+right+[ir.Cat(lr, rr, opres)])
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
                elif iname == "LOR":
                    return (opres, left+right+[ir.LOr(lr, rr, opres)])
                elif iname == "LAND":
                    return (opres, left+right+[ir.LAnd(lr, rr, opres)])
                elif iname == "OR":
                    return (opres, left+right+[ir.Or(lr, rr, opres)])
                elif iname == "AND":
                    return (opres, left+right+[ir.And(lr, rr, opres)])
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
            elif root.data == "member" or root.data == "range" or root.data == "slice":
                insts = self.generate_ir(root, True)
                return (insts[-1].dst, insts)
                
    def op_assign(self, dst, value, op):
        """
        Returns correct operation or assignment based on used operator
        E.g.: a = 4 vs a += 4
        """
        if op == "=":
            self.symb_table.assign(dst, value)
            if type(dst) != types.MultiVar:
                return ir.AssignVar(dst, value)
            else:
                return ir.AssignMultiple(dst.names, value)
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
        elif op == "++=":
            return ir.Cat(dst, value, dst)
        else:
            raise mex.InternalError("Somehow an unknown composit assignment was generated")

    def find_module(self, name):
        pname = Path(name)
        for base in self.opts.lib_path:
            fp = base / pname
            if fp.exists() and fp.is_file():
                return fp
        return None

    def import_module(self, scope, alias):
        if type(scope) == list:
            f_name = scope[0]+".ms"
        else:
            f_name = scope+".ms"
        lpath = self.find_module(f_name)
        if lpath is None:
            raise mex.ImportError("No module '"+f_name+"' found on lib path ("+(", ".join(["'"+str(i)+"'" for i in self.opts.lib_path]))+")")
        # Reading the file
        try:
            with open(lpath, 'r', encoding='utf-8') as lib_file:
                lib_code = lib_file.read()
        except PermissionError:
            raise mex.ImportError("Insufficient permissions to read file '"+str(lpath)+"'")
        except Exception:
            raise mex.ImportError("Could not read module file '"+str(lpath)+"'")
        
        if type(scope) != list:
            lib_code = "space "+alias+"{ " + lib_code + "}"
        else:
            sp_name = "__"+scope[0]
            # Name that cannot be accessed by the user
            lib_code = "space "+sp_name+"{ " + lib_code + "}"
        parser = Parser(lib_code, self.opts)
        tree = parser.parse()
        interpreter = Interpreter(self.opts, self.symb_table)
        lib_ir = interpreter.interpret_top_level(parsing.ConstTransformer(self.symb_table).transform(tree))
        if type(scope) == list:
            lib_ir.append(ir.AssignVar(alias, [sp_name]+scope[1:]))
        return lib_ir

    def generate_fun(self, root):
        insts = []
        tree = root.children
        name = tree[0].value
        if type(name) == list and type(name[0]) != str:
            insts += self.generate_ir(Token("scope_name", name), True)
            name = insts[-1].dst
        args = tree[1].value
        for i, a in enumerate(args):
            if type(a) == list and len(a) > 0 and type(a[0]) == str:
                args[i] = a
            elif type(a) == list:
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
            elif type(a) == Tree and (a.data == "member" or a.data == "range"):
                retv, inst_extra = self.generate_subexpr(a)
                insts += inst_extra
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
        else:
            return self.generate_fun(root)

    def generate_ir(self, root, silent=False):
        """
        Generates internal IR from parse tree
        """
        debug(root, self.opts)
        # Declaration or print
        if type(root) == Token:
            insts = []
            # Variable declaration or print
            if root.type == "VAR_NAME":
                self.symb_table.assign(root.value, ir.Nil())
                if not silent:
                    insts = [ir.SetOrPrint(root.value, ir.Nil(), output_file=self.output_file, output_format=self.output_format)]
                else:
                    insts += [ir.SetIfNotSet(root.value, ir.Nil())]
            # Printing
            elif root.type == "scope_name":
                # Value cannot be checked since it can be assigned in a class method or as an alias
                sc = []
                for v in root.value:
                    if type(v) == Token and v.type == "CODE":
                        insts += self.generate_ir(v, True)
                        sc.append(insts[-1].dst)
                    elif type(v) == list:
                        insts += v.value
                    else:
                        if type(v) == Token:
                            sc += v.value
                        else:
                            sc.append(v)
                if not silent:
                    insts += [ir.Print(sc, output_file=self.output_file, output_format=self.output_format)]
                else:
                    insts += [ir.AssignVar(sc, sc)]
            # Generated calculation
            elif root.type == "CALC":
                insts = []
                subtree = root.value
                for i in subtree:
                    if i.type == "CODE":
                        for code_inst in i.value:
                            if type(code_inst) == Tree or type(code_inst) == Token:
                                insts += self.generate_ir(code_inst, True)
                            else:
                                insts.append(code_inst)
                    else:
                        if i.type in Interpreter.CONSTS:
                            if not silent:
                                insts.append(ir.Print(i.value, output_file=self.output_file, output_format=self.output_format))
            # Generated code
            elif root.type == "CODE":
                insts = []
                for i in root.value:
                    if type(i) == Tree or type(i) == Token:
                        insts += self.generate_ir(i, silent)
                    else:
                        insts.append(i)
                if not silent:
                    insts.append(ir.Print(root.value[-1].dst, output_file=self.output_file, output_format=self.output_format))
            # Const print
            elif root.type in Interpreter.CONSTS:
                if not silent:
                    insts = [ir.Print(root.value, output_file=self.output_file, output_format=self.output_format)]
            # Break
            elif root.value == "break":
                insts = [ir.Break()]
            # Continue
            elif root.value == "continue":
                insts = [ir.Continue()]
            # internal
            elif root.value == "internal":
                insts = [ir.Internal()]
            # Note
            elif root.type == "note":
                if root.value[0] == "n":
                    # Note instructions are generated only for main module
                    if self.main:
                        if len(symb_table.frames) > 1:
                            raise mex.IncorrectDefinition("Notes can appear only on the global scope")
                        # General note
                        insts = [ir.Note(root.value[1], self.output_file, self.output_format, self.output_notes)]
                elif root.value[0] == "d":
                    # Documentation
                    insts = [ir.Doc(root.value[1])]
                else:
                    # This should have been handeled in the parser
                    raise mex.InternalError(f"Unexpected note prefix '{root.value[0]}'")
            self.last_inst = insts
            return insts
        else:
            insts = []
            # Assignment
            if root.data == "assignment" or root.data == "op_assign":
                tree = root.children[1]
                op = "="
                if root.children[0].type != "scope_list":
                    value = root.children[0].value
                else:
                    value = types.MultiVar(root.children[0].value)
                if root.data == "op_assign":
                    tree = root.children[2]
                    op = root.children[1].value
                if type(tree) == Token:
                    if tree.type in Interpreter.CONSTS:
                        insts.append(self.op_assign(value, tree.value, op))
                    elif tree.type == "CODE":
                        for code_inst in tree.value:
                            if type(code_inst) == Tree or type(code_inst) == Token:
                                insts += self.generate_ir(code_inst, True)
                            else:
                                insts.append(code_inst)
                        last_dst = tree.value[-1].dst
                        insts += [self.op_assign(value, last_dst, op)]
                    elif tree.type == "CALC":
                        subtree = tree.value
                        for i in subtree:
                            if i.type == "CODE":
                                for code_inst in i.value:
                                    if type(code_inst) == Tree or type(code_inst) == Token:
                                        insts += self.generate_ir(code_inst, True)
                                    else:
                                        insts.append(code_inst)
                            else:
                                if i.type in Interpreter.CONSTS:
                                    insts.append(self.op_assign(value, i.value, op))
                                else:
                                    raise mex.InternalError("Unexpected type in assignment")
                    elif tree.type == "VAR_NAME" or tree.type == "scope_name":
                        insts.append(self.op_assign(value, tree.value, op))
                    else:
                        raise mex.InternalError("Assignment not implemented for such value")
                else:
                    if tree.data == "fun_call":
                        insts = self.generate_ir(tree, True)+[self.op_assign(value, SymbTable.RETURN_NAME, op)]
                    elif tree.data == "assignment":
                        if root.data == "op_assign":
                            raise mex.SyntaxError("Assignment cannot be chained with compound assignment")
                        assign = self.generate_ir(tree, True)
                        self.symb_table.assign(value, assign[-1].dst)
                        insts += assign+[ir.AssignVar(root.children[0].value, assign[-1].dst)]
                    elif tree.data == "member" or tree.data == "range":
                        insts += self.generate_ir(tree, True)
                        insts.append(self.op_assign(value, insts[-1].dst, op))
                    elif tree.data == "lambda":
                        insts += self.generate_ir(tree, True)
                        insts.append(self.op_assign(value, insts[-1].name, op))
                    else:
                        raise mex.InternalError("Assignment not implemented for such value")
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
            elif root.data == "annotation":
                inner = len(root.children) > 1 and type(root.children[1]) == Token and root.children[1].type == "INNER"
                raise mex.Unimplemented("Annotations are not yet implemented")
            # Import
            elif root.data == "import":
                for m in root.children:
                    if m.type == "VAR_NAME":
                        insts += self.import_module(m.value, m.value)
                    elif m.type == "scope_name":
                        insts +=self.import_module(m.value, m.value[-1])
                    else:
                        raise mex.InternalError("Unknwon module parsed type")
            elif root.data == "import_as":
                insts += self.import_module(root.children[0].value, root.children[1].value)
            # Space
            elif root.data == "space":
                if len(root.children) > 1:
                    name = root.children[0].value
                    space = 1
                else:
                    name = self.uniq_space()
                    space = 0
                symb_table.push_space(name)
                insts.append(ir.SpacePush(name))
                for tree in root.children[space:]:
                    insts += self.generate_ir(tree)
                insts.append(ir.SpacePop())
                symb_table.pop_space()
            # Class
            elif root.data == "class":
                extends = []
                start_i = 1
                if len(root.children) > 1:
                    if type(root.children[1]) == Token and type(root.children[1].type == "space_list"):
                        extends = root.children[1].value
                        start_i += 1
                symb_table.push_class(root.children[0].value, extends)
                insts.append(ir.ClassPush(root.children[0].value, extends))
                for tree in root.children[start_i:]:
                    insts += self.generate_ir(tree)
                insts.append(ir.ClassPop())
                symb_table.pop_class()
            # Enum
            elif root.data == "enum":
                name = root.children[0].value
                values = [types.EnumValue(x.value, name) for x in root.children[1:]]
                r = types.Enum(name, values)
                symb_table.assign(name, r)
                insts.append(ir.AssignVar(name, r))
            # Function call
            elif root.data == "fun_call":
                insts += self.multi_call(root)
                if not silent:
                    insts.append(ir.Print(SymbTable.RETURN_NAME, output_file=self.output_file, output_format=self.output_format))
            # List comprehention
            elif root.data == "list_comp":
                raise mex.Unimplemented("List comprehention is not yet implemented")
            # Range
            elif root.data == "range":
                start = root.children[0]
                second = None if len(root.children) == 2 else root.children[1]
                end = root.children[1] if len(root.children) == 2 else root.children[2]
                step = types.Int(1)
                if type(start) == Token:
                    if start.type == "CODE":
                        insts += start.value
                        start = insts[-1].dst
                    else:
                        start = start.value
                if type(second) == Token:
                    if second.type == "CODE":
                        insts += second.value
                        second_r = insts[-1].dst
                        step = self.uniq_var()
                        insts.append(ir.Sub(second_r, start, step))
                    else:
                        step = self.uniq_var()
                        insts.append(ir.Sub(second.value, start, step))
                if type(end) == Token:
                    if end.type == "CODE":
                        insts += end.value
                        end = insts[-1].dst
                    else:
                        end = end.value
                obj_var = self.uniq_var()
                insts += [ir.FunCall("Range", [start, end, step]), ir.AssignVar(obj_var, SymbTable.RETURN_NAME)]
                if not silent:
                    insts.append(ir.Print(obj_var, output_file=self.output_file, output_format=self.output_format))
            # If statement or elif part
            elif root.data == "if" or root.data == "elif":
                tree = root.children[0].children
                cnd, insts = self.generate_cond(tree[0])
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
                cnd, cnd_insts = self.generate_cond(tree[0])
                insts += cnd_insts
                if type(tree[1]) == Tree and tree[1].data != "code_block":
                    symb_table.push()
                t = self.generate_ir(tree[1])
                if type(tree[1]) == Tree and tree[1].data != "code_block":
                    symb_table.pop()
                insts.append(ir.While(cnd, cnd_insts, t))
            # Do while loop
            elif root.data == "do_while":
                tree = root.children[0].children
                if type(tree[0]) == Tree and tree[0].data != "code_block":
                    symb_table.push()
                t = self.generate_ir(tree[0])
                if type(tree[0]) == Tree and tree[0].data != "code_block":
                    symb_table.pop()
                cnd, cnd_insts = self.generate_cond(tree[1])
                insts.append(ir.DoWhile(t, cnd, cnd_insts))
            # For loop
            elif root.data == "for":
                tree = root.children[0].children
                i = tree[0].value
                for i_name in i:
                    symb_table.assign(i_name, types.Nil())
                l = None
                # list might be complex
                if type(tree[1]) == Token and tree[1].type == "CODE":
                        insts += tree[1].value
                        l = insts[-1].dst
                elif type(tree[1]) == Tree:
                    if tree[1].data == "fun_call":
                        insts += self.multi_call(tree[1])
                        l = self.uniq_var()
                        insts.append(ir.AssignVar(l, SymbTable.RETURN_NAME))
                    elif tree[1].data == "member" or tree[1].data == "range":
                        insts += self.generate_ir(tree[1], True)
                        l = insts[-1].dst
                    elif len(tree[1].data) > 5 and tree[1].data[0:5] == "EXPR_":
                        l, extra = self.generate_expr(tree[1])
                        insts += extra
                    else:
                        raise mex.InternalError("Unexpected expression in for loop")
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
            # Raise
            elif root.data == "raise":
                raise mex.Unimplemented("Exceptions are not yet implemented")
            # Try
            elif root.data == "try":
                raise mex.Unimplemented("Exceptions are not yet implemented")
            # Lambda
            elif root.data == "lambda":
                tree = root.children
                offs = 0
                if tree[0].type == "VAR_NAME":
                    name = tree[0].value
                    offs = 1
                else:
                    name = self.uniq_lambda()
                args = tree[offs].value
                symb_table.push()
                # Push args
                for k, v in args:
                    # typed var
                    if type(k) == tuple:
                        k = k[0]
                    symb_table.declare(k, v)
                body = self.generate_ir(tree[offs+1], silent=True)
                body.append(ir.Return(body[-1].dst))
                symb_table.pop()
                insts.append(ir.Fun(name, args, body))
            # Function
            elif root.data == "function":
                tree = root.children
                if tree[0].type == "FUN_OP":
                    name = "("+tree[0].value+")"
                else:
                    name = tree[0].value
                args = tree[1].value
                # fun_code_block does not push the frame itself
                symb_table.push()
                # Push args
                for k, v in args:
                    # typed var
                    if type(k) == tuple:
                        k = k[0]
                    symb_table.declare(k, v)
                body = self.generate_ir(tree[2])
                symb_table.pop()
                insts.append(ir.Fun(name, args, body))
            elif root.data == "constructor":
                tree = root.children
                name = tree[0].value
                args = tree[1].value
                # fun_code_block does not push the frame itself
                symb_table.push()
                # Push args
                for k, v in args:
                    if type(k) == tuple:
                        k = k[0]
                    symb_table.declare(k, v)
                body = self.generate_ir(tree[2])
                symb_table.pop()
                insts.append(ir.Constructor(name, args, body))
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
                            if type(i) == Token and i.type == "CODE":
                                insts += i.value
                            elif type(i) == Token and i.type in Interpreter.CONSTS:
                                insts.append(ir.AssignVar(self.uniq_var(), i.value))
                            elif type(i) == Token or type(i) == Tree:
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
                    insts += [ir.Print(resvar, output_file=self.output_file, output_format=self.output_format)]
            # Member []
            elif root.data == "member":
                src, extra_insts = self.generate_subexpr(root.children[0])
                insts += extra_insts
                index, extra_insts = self.generate_subexpr(root.children[1])
                insts += extra_insts
                dst = self.uniq_var()
                insts.append(ir.Member(src, index, dst))
                if not silent:
                    insts.append(ir.Print(dst, output_file=self.output_file, output_format=self.output_format))
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
                    insts.append(ir.Print(dst, output_file=self.output_file, output_format=self.output_format))
            self.last_inst = insts
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
        if self.output_file is not None:
            with open(self.output_file, "w", encoding="utf-8") as outf:
                ...
        for i in code:
            if self.code_blocks is not None and self.output_file is not None and type(i) == ir.Note:
                if len(self.code_blocks) > 0:
                    with open(self.output_file, "a", encoding="utf-8") as outf:
                        s = self.code_blocks.pop()
                        if len(s) > 0 and not s.isspace():
                            outf.write("\n```\n"+s.strip()+"\n```\n")
                            if len(ir.output_print) > 0:
                                outstdp = "".join(ir.output_print)
                                outf.write("_[Output]:_\n```\n"+outstdp+"\n```\n")
                                ir.output_print = []
                else:
                    raise mex.InternalError("Somehow notes were incorrectly parsed in source code")
            i.exec()
        if self.code_blocks is not None and len(self.code_blocks) > 0 and self.output_file is not None:
            with open(self.output_file, "a", encoding="utf-8") as outf:
                    outf.write("```\n"+self.code_blocks.pop().strip()+"\n```\n")
                    if len(ir.output_print) > 0:
                        outstdp = "".join(ir.output_print)
                        outf.write("_[Output]:_\n```\n"+outstdp+"\n```\n")
                        ir.output_print = []

def format_ir(ir_code):
    for i in ir_code:
        print(i.output())

def interpret(opts, code, libmash_code):
    """
    Interpret mash code
    """
    debug("Parser started", opts)
    parser = Parser(code, opts)
    tree = parser.parse(main=True)
    code_blocks = parser.code_blocks[:]
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
        lib_parse = parsing.ConstTransformer(symb_table)
        lpt_tree = lib_parse.transform(libmash_tree)
        lib_code = lib_parse.insts
        lib_code += interpreter.interpret_top_level(lpt_tree)
    debug("Libmash code generated", opts)
    ir_parse = parsing.ConstTransformer(symb_table)
    ir_tree = ir_parse.transform(tree)
    ir_code = ir_parse.insts
    interpreter.main = True
    ir_code += interpreter.interpret_top_level(ir_tree)
    debug("IR generation done", opts)
    if opts.code_only:
        format_ir(ir_code)
        return
    debug("Running IR", opts)
    symb_table.clear_all()
    if not opts.no_libmash:
        interpreter.interpret(lib_code)
    interpreter.code_blocks = code_blocks
    interpreter.interpret(ir_code)
    interpreter.main = False
    debug("Finished running IR", opts)
    
