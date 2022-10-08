from symbol_table import symb_table
from mash import Mash
import mash_exceptions as mex
from mash_types import Float, Int, Nil, Bool, String, Value, List, RString, FString

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
        pass

    def str_header(self):
        args = []
        for k, v in self.args:
            if v is None:
                args.append(str(k))
            else:
                args.append(f"{k} = {v}")
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
                args.append(f"{k} = {v}")
        args_s = ", ".join(args)
        return f"FUN {self.name}({args_s}) {{\n{t}\n}}"

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
        if issubclass(type(s1), String) or issubclass(type(s2), String):
            v1 = str(v1)
            v2 = str(v2)
        else:
            self.check_types("+", s1, s2, {Int, Float, String, RString, FString, List})
        r = v1+v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"ADD {self.src1}, {self.src2}, {self.dst}"

class Sub(Expr):
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
        self.check_types("-", s1, s2, {Int, Float})
        r = v1-v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"SUB {self.src1}, {self.src2}, {self.dst}"
