from ast import ClassDef
from typing import Type
from symbol_table import symb_table, SymbTable, ClassFrame, Frame, SpaceFrame
import mash_exceptions as mex
from mash_types import Float, Int, Nil, Bool, String, Value, List, Dict
import mash_types as types
import libmash

class IR:
    """
    Base class for all ir nodes
    """
    SPCS = "    "

    def getV(self, name):
        if type(name) == str or type(name) == list:
            return symb_table.get(name).get_value()
        elif issubclass(type(name), Value):
            return name.get_value()

    def get(self, name):
        if type(name) == str or type(name) == list:
            return symb_table.get(name)
        elif issubclass(type(name), Value):
            return name
        elif type(name) == ClassFrame or type(name) == SpaceFrame:
            return str(name)
        else:
            raise mex.Unimplemented("Getter for IR node type")

    def output(self, indent=0):
        return (indent*IR.SPCS)+str(self)

def wrap(v):
    if type(v) == int:
        return Int(v)
    elif type(v) == float:
        return Float(v)
    elif type(v) == str:
        return String(v, escape_chs=False)
    elif type(v) == bool:
        return Bool(v)
    elif type(v) == list:
        return List(v)
    elif v is None:
        return Nil(v)
    else:
        raise mex.Unimplemented(f"Wrapper for type '{type(v)}'")

def ir_str(value):
    if type(value) == list:
        return "".join(value)
    elif type(value) == str:
        return value
    else:
        return value.ir_str()

class Instruction(IR):
    """
    Base class for all instructions
    """

    def exec(self):
        """
        Method to be overrriden by an instruction
        """
        # TODO: Change to exception
        print("MISSING EXEC METHOD")

    def call(self):
        """
        Method to be overriden by instructions that are callable
        """
        print("MISSING CALL METHOD")

    def update(self, v):
        if issubclass(type(v), Value):
            v.update()

class AssignVar(Instruction):
    """
    Variable declaration and definition
    """
    def __init__(self, dst, value):
        self.dst = dst
        self.value = value

    def exec(self):
        self.update(self.value)
        symb_table.assign(self.dst, self.value)

    def __str__(self):
        return f"SET {ir_str(self.value)}, {ir_str(self.dst)}"

class Print(Instruction):
    """
    Variable declaration and definition
    """
    def __init__(self, value):
        self.value = value

    def exec(self):
        self.update(self.value)
        v = self.get(self.value)
        if type(v) == list:
            # Function/s (there can be multiple)
            print(v[0].fstr(), end="")
        else:
            print(v, end="")

    def __str__(self):
        return f"PRINT {ir_str(self.value)}"

class SetIfNotSet(Instruction):
    """
    If variable is not yet set, then this declares it,
    if it is set, then it prints it
    """
    def __init__(self, dst, value=Nil()):
        self.dst = dst
        self.value = value

    def exec(self):
        s, _ = symb_table.exists(self.dst)
        if not s:
            symb_table.assign(self.dst, self.value)

    def __str__(self):
        return f"SETIFNOTSET {ir_str(self.value)}, {self.dst}"

class SetOrPrint(Instruction):
    """
    If variable is not yet set, then this declares it,
    if it is set, then it prints it
    """
    def __init__(self, dst, value=Nil()):
        self.dst = dst
        self.value = value

    def exec(self):
        s, _ = symb_table.exists(self.dst)
        if not s:
            self.update(self.value)
            symb_table.assign(self.dst, self.value)
        else:
            self.update(self.dst)
            v = self.get(self.dst)
            if type(v) == list:
                # Function/s (there can be multiple)
                print(v[0].fstr(), end="")
            else:
                print(v, end="")

    def __str__(self):
        return f"SETORPRINT {ir_str(self.value)}, {self.dst}"

class ToString(Instruction):
    """
    Convert value to a string
    """
    def __init__(self, value, dst):
        self.dst = dst
        self.value = value

    def exec(self):
        v = self.get(self.value)
        symb_table.assign(self.dst, String(str(v)))

    def __str__(self):
        return f"TOSTR {ir_str(self.value)}, {self.dst}"

class ListWrap(Instruction):
    """
    Wrap value as a list
    """
    def __init__(self, value, dst):
        self.dst = dst
        self.value = value

    def exec(self):
        v = self.get(self.value)
        symb_table.assign(self.dst, List([v]))

    def __str__(self):
        return f"LISTWRAP {ir_str(self.value)}, {self.dst}"

class Nop(Instruction):
    """
    No operation
    """
    def __init__(self):
        pass

    def exec(self):
        pass

    def __str__(self):
        return "NOP"

class If(Instruction):
    """
    If statement
    """
    def __init__(self, cnd, t, f):
        self.cnd = cnd
        self.t = t
        if type(self.t) is not list:
            self.t = [self.t]
        self.f = f
        if type(self.f) is not list:
            self.f = [self.f]

    def exec(self):
        symb_table.push()
        c = self.getV(self.cnd)
        try:
            if c:
                for i in self.t:
                    i.exec()
            else:
                for i in self.f:
                    i.exec()
        except mex.FlowControlReturn as e:
            raise mex.FlowControlReturn(e.value, e.frames+1)
        symb_table.pop()

    def output(self, indent=0):
        t = self.t
        f = self.f
        if type(self.t) == list:
            t = "\n".join(i.output(indent+1) for i in t)
        if type(self.f) == list:
            f = "\n".join(i.output(indent+1) for i in f)
        spc = (indent*IR.SPCS)
        return spc+f"IF ({self.cnd}) {{\n{t}\n{spc}}} ELSE {{\n{f}\n{spc}}}"

    def __str__(self):
        t = self.t
        f = self.f
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        if type(self.f) == list:
            f = "\n".join(str(i) for i in f)
        return f"IF ({self.cnd}) {{\n{t}\n}} ELSE {{\n{f}\n}}"

class While(Instruction):
    """
    While loop
    """
    def __init__(self, cnd, cnd_insts, t):
        self.cnd = cnd
        self.cnd_insts = cnd_insts
        self.t = t
        if type(self.t) is not list:
            self.t = [self.t]

    def exec(self):
        symb_table.push()
        c = self.getV(self.cnd)
        while c:
            try:
                for i in self.t:
                    i.exec()
            except mex.FlowControlBreak:
                break
            except mex.FlowControlContinue:
                continue
            except mex.FlowControlReturn as e:
                raise mex.FlowControlReturn(e.value, e.frames+1)
            # Run code for condition
            for i in self.cnd_insts:
                i.exec()
            c = self.getV(self.cnd)
        symb_table.pop()

    def output(self, indent=0):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(i.output(indent+1) for i in t)
        spc = indent*IR.SPCS
        return spc+f"WHILE ({self.cnd}) {{\n{t}\n{spc}}}"

    def __str__(self):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        return f"WHILE ({self.cnd}) {{\n{t}\n}}"

class DoWhile(Instruction):
    """
    Do While loop
    """
    def __init__(self, t, cnd, cnd_insts):
        self.cnd = cnd
        self.cnd_insts = cnd_insts
        self.t = t
        if type(self.t) is not list:
            self.t = [self.t]

    def exec(self):
        symb_table.push()
        try:
            for i in self.t:
                i.exec()
        except mex.FlowControlBreak:
            symb_table.pop()
            return
        except mex.FlowControlContinue:
            ...
        except mex.FlowControlReturn as e:
            raise mex.FlowControlReturn(e.value, e.frames+1)
        # Run code for condition
        for i in self.cnd_insts:
            i.exec()
        c = self.getV(self.cnd)
        while c:
            try:
                for i in self.t:
                    i.exec()
            except mex.FlowControlBreak:
                break
            except mex.FlowControlContinue:
                continue
            except mex.FlowControlReturn as e:
                raise mex.FlowControlReturn(e.value, e.frames+1)
            # Run code for condition
            for i in self.cnd_insts:
                i.exec()
            c = self.getV(self.cnd)
        symb_table.pop()

    def output(self, indent=0):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(i.output(indent+1) for i in t)
        spc = IR.SPCS*indent
        return spc+f"DO {{\n{t}\n{spc}}} WHILE ({self.cnd})"

    def __str__(self):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        return f"DO {{\n{t}\n}} WHILE ({self.cnd})"

class For(Instruction):
    """
    For loop
    """
    def __init__(self, i, l, t):
        self.i = i
        self.l = l
        self.t = t
        if type(self.t) is not list:
            self.t = [self.t]

    def exec(self):
        symb_table.push()
        s = self.get(self.l)
        if type(s) != List and type(s) != Dict:
            raise mex.TypeError(f"Cannot iterate over {s.type_name()}")
        v = s.get_value()
        if type(s) == Dict:
            v = s.items().get_value()
        for a in v:
            symb_table.assign(self.i, a)
            try:
                for i in self.t:
                    i.exec()
            except mex.FlowControlBreak:
                break
            except mex.FlowControlContinue:
                continue
            except mex.FlowControlReturn as e:
                symb_table.pop()
                raise e
        symb_table.pop()

    def output(self, indent=0):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(i.output(indent+1) for i in t)
        spc = IR.SPCS*indent
        return spc+f"FOR ({self.i} : {self.l}) {{\n{t}\n{spc}}}"

    def __str__(self):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        return f"FOR ({self.i} : {self.l}) {{\n{t}\n}}"

class Internal(IR):
    """
    Internal implementation
    """
    def __str__(self):
        return "internal"

class Fun(Instruction):
    """
    Function
    """
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.req_args = [k for k, v in args if v is None]
        self.min_args = len(self.req_args)
        self.max_args = len(self.args)
        self.body = body
        self.internal = False
        if len(self.body) > 0 and type(self.body[0]) == Internal:
            self.internal = True
            try:
                self.body = getattr(libmash, name+"_"+str(len(args)))
            except AttributeError:
                raise mex.UndefinedReference(self.str_header())

    def exec(self):
        # Exec is for definition
        symb_table.define_fun(self.name, self.min_args, self.max_args, self)

    def wrap_internal(self, v):
        """
        Wraps value returned by internal function into IR value if not yet wrapped
        """
        if   type(v) == int: return types.Int(v)
        elif type(v) == float: return types.Float(v)
        elif type(v) == str: return types.String(v)
        elif type(v) == list: return types.List(v)
        elif type(v) == bool: return types.Bool(v)
        elif v is None: return types.Nil()
        else: return v

    def call(self):
        if self.internal:
            assign_args = []
            for a, _ in self.args:
                assign_args.append(symb_table.get(a).get_value())
            try:
                rval = self.wrap_internal(self.body(*assign_args))
            except TypeError:
                raise mex.TypeError("Incorrect argument type in function call to '"+self.str_header()+"'")
            return rval, 1
        else:
            for i in self.body:
                try:
                    i.exec()
                except mex.FlowControlReturn as r:
                    return r.value, r.frames
            return types.Nil(), 1

    def str_header(self):
        args = []
        for k, v in self.args:
            if v is None:
                args.append(str(k))
            else:
                args.append(f"{k} = {str(v)}")
        args_s = ", ".join(args)
        return f"fun {self.name}({args_s})"+(" internal" if self.internal else "")

    def fstr(self):
        details = ""
        v = symb_table.get(self.name)
        if len(v) > 1:
            details = f" with {len(v)} signatures"
        n = "".join(self.name)
        return f"<function '{n}'{details}>"

    def output(self, indent=0):
        if self.internal:
            return self.str_header()
        t = self.body
        if type(self.body) == list:
            t = "\n".join(i.output(indent+1) for i in t)
        args = []
        for k, v in self.args:
            if v is None:
                args.append(str(k))
            else:
                args.append(f"{k} = {str(v)}")
        args_s = ", ".join(args)
        n = "".join(self.name)
        spc = IR.SPCS*indent
        return spc+f"fun {n}({args_s}) {{\n{t}\n{spc}}}"

    def __str__(self):
        if self.internal:
            return self.str_header()
        t = self.body
        if type(self.body) == list:
            t = "\n".join(str(i) for i in t)
        args = []
        for k, v in self.args:
            if v is None:
                args.append(str(k))
            else:
                args.append(f"{k} = {str(v)}")
        args_s = ", ".join(args)
        n = "".join(self.name)
        return f"fun {n}({args_s}) {{\n{t}\n}}"

class Constructor(Fun):
    """
    Class constructor
    """
    def __init__(self, name, args, body):
        if len(args) < 1:
            raise mex.TypeError("Constructor has to take at least one argument - the object itself")
        super(Constructor, self).__init__(name, args, body)

    def call(self):
        if self.internal:
            assign_args = []
            for a, _ in self.args:
                assign_args.append(symb_table.get(a).get_value())
            try:
                rval = self.wrap_internal(self.body(*assign_args))
            except TypeError:
                raise mex.TypeError("Incorrect argument type in function call to '"+self.str_header()+"'")
            return self.args[0][1], 1
        else:
            for i in self.body:
                try:
                    i.exec()
                except mex.FlowControlReturn as r:
                    if type(r.value) != Nil:
                        raise mex.TypeError("Constructor has to return nil")
                    return r.value, r.frames
            return symb_table.get(self.args[0][0]), 1

    def str_header(self):
        args = []
        for k, v in self.args:
            if v is None:
                args.append(str(k))
            else:
                args.append(f"{k} = {str(v)}")
        args_s = ", ".join(args)
        return f"new {self.name}({args_s})"+(" internal" if self.internal else "")

    def output(self, indent=0):
        if self.internal:
            return self.str_header()
        t = self.body
        if type(self.body) == list:
            t = "\n".join(i.output(indent+1) for i in t)
        args = []
        for k, v in self.args:
            if v is None:
                args.append(str(k))
            else:
                args.append(f"{k} = {str(v)}")
        args_s = ", ".join(args)
        n = "".join(self.name)
        spc = IR.SPCS*indent
        return spc+f"new {n}({args_s}) {{\n{t}\n{spc}}}"

    def __str__(self):
        if self.internal:
            return self.str_header()
        t = self.body
        if type(self.body) == list:
            t = "\n".join(str(i) for i in t)
        args = []
        for k, v in self.args:
            if v is None:
                args.append(str(k))
            else:
                args.append(f"{k} = {str(v)}")
        args_s = ", ".join(args)
        n = "".join(self.name)
        return f"new {n}({args_s}) {{\n{t}\n}}"


class FunCall(Instruction):
    """
    Function call
    """
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.pos_args = []
        self.named_args = []
        for i in self.args:
            if type(i) != tuple:
                self.pos_args.append(i)
            else:
                self.named_args.append(i)

    def exec(self):
        lframe = None
        method_call = False
        if type(self.name) == list and len(self.name) > 2 and self.name[-2] == ".":
            method_call = True
            frame = symb_table.get_frame(self.name, flist=True)
            if frame is not None:
                i = len(frame)
                while i >= 0:
                    i -= 1
                    frm = frame[i]
                    if not issubclass(type(frm), Frame):
                        continue
                    if frm in symb_table.frames:
                        lframe = frm
                frame = frame[-1].frame
        else:
            frame = symb_table.get_frame(self.name)

        if frame is None:
            fl = None
        else:
            if type(self.name) == list:
                n = self.name[-1]
            else:
                n = self.name
            fl = frame[n]
        if fl is None:
            raise mex.UndefinedReference("".join(self.name))
        if type(fl) != list and type(fl) != ClassFrame:
            if self.name[0] == "$":
                raise mex.TypeError("Type '"+types.type_name(fl)+"' is not callable")
            else:
                raise mex.TypeError("'"+"".join(self.name)+"' is not callable")
        f = None
        new_obj = False
        if type(fl) == ClassFrame:
            new_obj = True
            n = fl.name
            if n not in fl:
                raise mex.Unimplemented("Implicit constructors")
                ... # TODO: implicit constructor
            else:
                for i in fl[n]:
                    # Find matching function signature
                    if i.max_args-1 >= len(self.args):
                        f = i
                        break
                if f is None:
                    raise mex.UndefinedReference(f"Arguments do not match any class '{self.name}' constructors")
        else:
            for i in fl:
                # Find closest matching function signature
                if i.max_args >= len(self.args):
                    f = i
                    break
            if f is None:
                if self.name[0] == "$":
                    raise mex.UndefinedReference(f"Arguments do not match any function's '{fl[0].name}' signatures")
                else:
                    raise mex.UndefinedReference(str(self))
            elif type(f) == Constructor:
                raise mex.TypeError("Constructor cannot be called as a function")
        assigned = []
        start_arg_i = 0
        if new_obj:
            assigned = [(f.args[0][0], fl.instance())]
            start_arg_i = 1
        elif method_call:
            assigned = [(f.args[0][0], self.name[-3])]
            start_arg_i = 1
        for i, a in enumerate(f.args[start_arg_i:]):
            v = a[1]
            a = a[0]
            if i >= len(self.pos_args):
                if v is None:
                    raise mex.TypeError(f"Function call to '{f.str_header()}' is missing required positional argument '{a}'")
                else:
                    break
            passed = self.pos_args[i]
            value = passed
            if type(passed) == str or type(passed) == list: 
                # Variable
                value = symb_table.get(passed)
            assigned.append((a, value))

        for k, v in self.named_args:
            for a, b in f.args:
                if b is not None:
                    assigned.append((k, v))
                    break
            else:
                n = "".join(self.name)
                raise mex.TypeError(f"Argument named '{k}' in function call to '{n}' not found")
        # Move stack of frame top to the callee frame
        prev_top = symb_table.top()
        if lframe is not None:
            symb_table.move_top(lframe)
        elif frame in symb_table.frames:
            symb_table.move_top(frame)
        else:
            lframe = symb_table.get_frame(self.name, flist=True)
            # There is a chance that the function is nested and then
            # we need to get the lowest level frame
            for frm in reversed(lframe):
                if frm in symb_table.frames:
                    symb_table.move_top(frm)
        # Push new frame and arguments
        symb_table.push(True)
        # Set default args
        for k, v in f.args:
            if v is not None:
                symb_table.assign(k, v)
        for k, v in assigned:
            symb_table.assign(k, v)
        ret_val, frames = f.call()
        if type(ret_val) == str:
            ret_val = symb_table.get(ret_val)
        #print(symb_table, "\n---\n")
        symb_table.pop(frames)
        symb_table.move_top(prev_top)
        symb_table.assign(SymbTable.RETURN_NAME, ret_val)

    def __str__(self):
        args = []
        for k in self.args:
            if type(k) != tuple:
                args.append(str(k))
            else:
                args.append(f"{k[0]} = {str(k[1])}")
        args_s = ", ".join(args)
        n = "".join(self.name)
        return f"{n}({args_s})"

class Member(Instruction):
    """
    Member operator
    """

    def __init__(self, src, index, dst):
        self.src = src
        self.dst = dst
        self.index = index

    def exec(self):
        s1 = self.get(self.src)
        if type(s1) == list:
            raise mex.TypeError("Functions are not subscriptable")
        v = s1._at(self.get(self.index))
        symb_table.assign(self.dst, v)

    def __str__(self):
        return f"AT {ir_str(self.src)}, {ir_str(self.index)}, {self.dst}"

class Slice(Instruction):
    """
    Slice operator
    """

    def __init__(self, src, i1, i2, step, dst):
        self.src = src
        self.dst = dst
        self.i1 = i1
        self.i2 = i2
        self.step = step

    def exec(self):
        s1 = self.get(self.src)
        if type(s1) == list:
            raise mex.TypeError("Functions cannot be sliced")
        v = s1._slice(self.get(self.i1), self.get(self.i2), self.get(self.step))
        symb_table.assign(self.dst, v)

    def __str__(self):
        return f"SLICE {ir_str(self.src)}, {ir_str(self.i1)}, {ir_str(self.i2)}, {ir_str(self.step)}, {self.dst}"

class SpacePush(Instruction):
    """
    Starts namespace
    """
    def __init__(self, name):
        self.name = name

    def exec(self):
        symb_table.push_space(self.name)

    def __str__(self):
        return f"SPCPUSH {self.name}"

class SpacePop(Instruction):
    """
    Ends namespace
    """
    def __init__(self):
        ...

    def exec(self):
        symb_table.pop_space()

    def __str__(self):
        return "SPCPOP"

class ClassPush(Instruction):
    """
    Starts class definition
    """
    def __init__(self, name):
        self.name = name

    def exec(self):
        symb_table.push_class(self.name)

    def __str__(self):
        return f"CLSPUSH {self.name}"

class ClassPop(Instruction):
    """
    Ends class definition
    """
    def __init__(self):
        ...

    def exec(self):
        symb_table.pop_class()

    def __str__(self):
        return "CLSPOP"

class Keyword(Instruction):
    """
    Keyword instruction
    """

class Break(Keyword):
    """
    Break
    """
    def exec(self):
        raise mex.FlowControlBreak()

    def __str__(self):
        return "break"

class Continue(Keyword):
    """
    Continue
    """
    def exec(self):
        raise mex.FlowControlContinue()

    def __str__(self):
        return "continue"

class Return(Keyword):
    """
    Return
    """
    def __init__(self, value):
        self.value = value

    def exec(self):
        raise mex.FlowControlReturn(self.get(self.value))

    def __str__(self):
        return "return "+str(self.value)
        
class Expr(IR):
    """
    Expression
    """
    def check_types(self, op, s1, s2, allowed):
        if type(s1) == list:
            s1 = s1[0].fstr()
        if type(s2) == list:
            s2 = s2[0].fstr()
        if (type(s1) == str or type(s2) == str) or not ((type(s1) in allowed) and (type(s2) in allowed)):
            raise mex.TypeError(f"Unsupported types for '{op}'. Given values are '{s1}' and '{s2}'")

class TernaryIf(Expr):
    """
    Ternary If
    """
    def __init__(self, cnd, t, f, dst):
        self.cnd = cnd
        self.t = t
        self.f = f
        self.dst = dst

    def exec(self):
        c = self.getV(self.cnd)
        if c:
            symb_table.assign(self.dst, self.t)
        else:
            symb_table.assign(self.dst, self.f)

    def __str__(self):
        return f"TIF {self.cnd}, {self.t}, {self.f}, {self.dst}"

class Mul(Expr):
    """
    Multiplication
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("*", s1, s2, {Int, Float})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1*v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"MUL {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Add(Expr):
    """
    Addition
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("+", s1, s2, {Int, Float, String, List, Dict})
        if issubclass(type(s1), String) or issubclass(type(s2), String):
            v1 = str(s1)
            v2 = str(s2)
        else:
            v1 = s1.get_value()
            v2 = s2.get_value()
        r = v1+v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"ADD {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Sub(Expr):
    """
    Subtraction
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("-", s1, s2, {Int, Float})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1-v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"SUB {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class FDiv(Expr):
    """
    Float division
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("/", s1, s2, {Int, Float})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1/v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"FDIV {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class IDiv(Expr):
    """
    Int division
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("//", s1, s2, {Int, Float})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1//v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"IDIV {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Mod(Expr):
    """
    Int division
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("%", s1, s2, {Int, Float})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1 % v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"MOD {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Exp(Expr):
    """
    Exponentiation
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("^", s1, s2, {Int, Float})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1 ** v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"EXP {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class In(Expr):
    """
    In collection
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        r = s2._in(s1)
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"IN {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class LOr(Expr):
    """
    Logical OR
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        if type(s1) in types.IMPLICIT_TO_BOOL:
            v1 = bool(v1.get_value())
            s1 = types.Bool(v1)
        else:
            v1 = s1.get_value()
        if type(s2) in types.IMPLICIT_TO_BOOL:
            v2 = bool(v2.get_value())
            s2 = types.Bool(v2)
        else:
            v2 = s2.get_value()
        self.check_types("or", s1, s2, {Bool})
        r = v1 or v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"OR {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class LAnd(Expr):
    """
    Logical AND
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        if type(s1) in types.IMPLICIT_TO_BOOL:
            v1 = bool(v1.get_value())
            s1 = types.Bool(v1)
        else:
            v1 = s1.get_value()
        if type(s2) in types.IMPLICIT_TO_BOOL:
            v2 = bool(v2.get_value())
            s2 = types.Bool(v2)
        else:
            v2 = s2.get_value()
        self.check_types("and", s1, s2, {Bool})
        r = v1 and v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"AND {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class LNot(Expr):
    
    def __init__(self, src1, dst):
        self.dst = dst
        self.src1 = src1

    def exec(self):
        s1 = self.get(self.src1)
        if type(s1) in types.IMPLICIT_TO_BOOL:
            v1 = bool(s1.get_value())
            s1 = types.Bool(v1)
        else:
            v1 = s1.get_value()
        self.check_types("not", s1, Bool(True), {Bool})
        r = not v1
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"NOT {ir_str(self.src1)}, {self.dst}"

class Lte(Expr):
    
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("<=", s1, s2, {Int, Float, String, Bool})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1 <= v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"LTE {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Gte(Expr):
    
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types(">=", s1, s2, {Int, Float, String, Bool})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1 >= v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"GTE {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Gt(Expr):
    
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types(">", s1, s2, {Int, Float, String, Bool})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1 > v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"GT {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Lt(Expr):
    
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("<", s1, s2, {Int, Float, String, Bool})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1 < v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"LT {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Eq(Expr):
    
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("==", s1, s2, {Int, Float, String, Bool, List, Dict})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1 == v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"EQ {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Neq(Expr):
    
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        self.check_types("!=", s1, s2, {Int, Float, String, Bool, List, Dict})
        v1 = s1.get_value()
        v2 = s2.get_value()
        r = v1 != v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"NEQ {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Inc(Expr):
    
    def __init__(self, dst):
        self.dst = dst

    def exec(self):
        s1 = self.get(self.dst)
        self.check_types("++", s1, Int(1), {Int, Float})
        v1 = s1.get_value()
        r = v1 + 1
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"INC {self.dst}"

class Dec(Expr):
    
    def __init__(self, dst):
        self.dst = dst

    def exec(self):
        s1 = self.get(self.dst)
        self.check_types("--", s1, Int(1), {Int, Float})
        v1 = s1.get_value()
        r = v1 - 1
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"DEC {self.dst}"
