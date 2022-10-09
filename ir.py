from symbol_table import symb_table, SymbTable
from mash import Mash
import mash_exceptions as mex
from mash_types import Float, Int, Nil, Bool, String, Value, List, RString, FString
import mash_types as types

class IR:
    """
    Base class for all ir nodes
    """
    def getV(self, name):
        if type(name) == str:
            return symb_table.get(name).get_value()
        elif issubclass(type(name), Value):
            return name.get_value()

    def get(self, name):
        if type(name) == str:
            return symb_table.get(name)
        elif issubclass(type(name), Value):
            return name

def wrap(v):
    if type(v) == int:
        return Int(v)
    elif type(v) == float:
        return Float(v)
    elif type(v) == str:
        return String(v)
    elif type(v) == bool:
        return Bool(v)
    elif v is None:
        return Nil(v)
    else:
        raise mex.Unimplemented(f"Wrapper for type '{type(v)}'")

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

class AssignVar(Instruction):
    """
    Variable declaration and definition
    """
    def __init__(self, dst, value):
        self.dst = dst
        self.value = value

    def exec(self):
        symb_table.assign(self.dst, self.value)

    def __str__(self):
        return f"SET {self.value}, {self.dst}"

class Print(Instruction):
    """
    Variable declaration and definition
    """
    def __init__(self, value, dst=Nil()):
        self.dst = dst
        self.value = value

    def exec(self):
        print(self.get(self.value), end="")

    def __str__(self):
        return f"PRINT {self.value}, {self.dst}"

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
        return f"TOSTR {self.value}, {self.dst}"

class Nop(Instruction):
    """
    No operation
    """
    def __init__(self):
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
        if c:
            for i in self.t:
                i.exec()
        else:
            for i in self.f:
                i.exec()
        symb_table.pop()

    def __str__(self):
        t = self.t
        f = self.f
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        if type(self.f) == list:
            f = "\n".join(str(i) for i in f)
        return f"IF ({self.cnd}) {{\n{t}\n}} ELSE {{\n{f}}}"

class While(Instruction):
    """
    While loop
    """
    def __init__(self, cnd, t):
        self.cnd = cnd
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
            c = self.getV(self.cnd)
        symb_table.pop()

    def __str__(self):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        return f"WHILE ({self.cnd}) {{\n{t}\n}}"

class DoWhile(Instruction):
    """
    Do While loop
    """
    def __init__(self, t, cnd):
        self.cnd = cnd
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
        c = self.getV(self.cnd)
        while c:
            try:
                for i in self.t:
                    i.exec()
            except mex.FlowControlBreak:
                break
            except mex.FlowControlContinue:
                continue
            c = self.getV(self.cnd)
        symb_table.pop()

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
        for a in self.l.get_value():
            symb_table.assign(self.i, a)
            try:
                for i in self.t:
                    i.exec()
            except mex.FlowControlBreak:
                break
            except mex.FlowControlContinue:
                continue
        symb_table.pop()

    def __str__(self):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        return f"FOR ({self.i} : {self.l}) {{\n{t}\n}}"

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

    def exec(self):
        # Exec is for definition
        symb_table.define_fun(self.name, self.min_args, self.max_args, self)

    def call(self):
        for i in self.body:
            try:
                i.exec()
            except mex.FlowControlReturn as r:
                return r.value
        return types.Nil()

    def str_header(self):
        args = []
        for k, v in self.args:
            if v is None:
                args.append(str(k))
            else:
                args.append(f"{k} = {str(v)}")
        args_s = ", ".join(args)
        return f"FUN {self.name}({args_s})"

    def __str__(self):
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
        return f"FUN {self.name}({args_s}) {{\n{t}\n}}"

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
        fl = symb_table.get(self.name)
        if type(fl) != list:
            raise mex.TypeError("'"+self.name+"' is not callable")
        f = None
        for i in fl:
            # Find matching function signature
            if i.max_args >= len(self.args):
                f = i
                break
        if f is None:
            raise mex.UndefinedReference(str(self))
        assigned = []
        for i, a in enumerate(f.args):
            v = a[1]
            a = a[0]
            if i >= len(self.pos_args):
                if v is None:
                    raise mex.TypeError(f"Function call to '{self.name}' is missing required positional argument '{a}'")
                else:
                    break
            passed = self.pos_args[i]
            value = passed
            if type(passed) == str: 
                # Variable
                value = symb_table.get(passed)
            assigned.append((a, value))

        for k, v in self.named_args:
            for a, b in f.args:
                if b is not None:
                    assigned.append((k, v))
                    break
            else:
                raise mex.TypeError(f"Argument named '{k}' in function call to '{self.name}' not found")
        # Push new frame and arguments
        symb_table.push()
        # Set default args
        for k, v in f.args:
            if v is not None:
                symb_table.assign(k, v)
        for k, v in assigned:
            symb_table.assign(k, v)
        ret_val = f.call()
        symb_table.pop()
        symb_table.assign(SymbTable.RETURN_NAME, ret_val)

    def __str__(self):
        args = []
        for k in self.args:
            if type(k) != tuple:
                args.append(str(k))
            else:
                args.append(f"{k[0]} = {str(k[1])}")
        args_s = ", ".join(args)
        return f"{self.name}({args_s})"

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
        raise mex.FlowControlReturn(self.value)

    def __str__(self):
        return "return "+str(self.value)
        
class Expr(IR):
    """
    Expression
    """
    def check_types(self, op, s1, s2, allowed):
        if not ((type(s1) in allowed) and (type(s2) in allowed)):
            raise mex.TypeError(f"Unsupported types for '{op}'. Given values are '{s1}' and '{s2}'.")

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
        v1 = s1.get_value()
        v2 = s2.get_value()
        self.check_types("*", s1, s2, {Int, Float})
        r = v1*v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"MUL {self.src1}, {self.src2}, {self.dst}"

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
        v1 = s1.get_value()
        v2 = s2.get_value()
        if issubclass(type(s1), String) or issubclass(type(s2), String):
            v1 = str(s1)
            v2 = str(s2)
        else:
            self.check_types("+", s1, s2, {Int, Float, String, RString, FString, List})
        r = v1+v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"ADD {self.src1}, {self.src2}, {self.dst}"

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
        v1 = s1.get_value()
        v2 = s2.get_value()
        self.check_types("-", s1, s2, {Int, Float})
        r = v1-v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"SUB {self.src1}, {self.src2}, {self.dst}"

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
        v1 = s1.get_value()
        v2 = s2.get_value()
        if type(s1) in types.IMPLICIT_TO_BOOL:
            v1 = bool(v1)
            s1 = types.Bool(v1)
        if type(s2) in types.IMPLICIT_TO_BOOL:
            v2 = bool(v2)
            s2 = types.Bool(v2)
        self.check_types("or", s1, s2, {Bool})
        r = v1 or v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"OR {self.src1}, {self.src2}, {self.dst}"

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
        v1 = s1.get_value()
        v2 = s2.get_value()
        if type(s1) in types.IMPLICIT_TO_BOOL:
            v1 = bool(v1)
            s1 = types.Bool(v1)
        if type(s2) in types.IMPLICIT_TO_BOOL:
            v2 = bool(v2)
            s2 = types.Bool(v2)
        self.check_types("and", s1, s2, {Bool})
        r = v1 and v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"AND {self.src1}, {self.src2}, {self.dst}"

"""
class (Expr):
    
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        v1 = s1.get_value()
        v2 = s2.get_value()
        self.check_types("", s1, s2, {Int, Float})
        r = v1 v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f" {self.src1}, {self.src2}, {self.dst}"
"""