from symbol_table import symb_table
from mash import Mash
import mash_exceptions as mex
from mash_types import Float, Int, Nil, Bool, String, Value

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
        raise mex.Unimplemented(f"Unimplemented wrapper for type '{type(v)}'")

class Instruction(IR):
    """
    Base class for all instructions
    """

    def exec(self):
        """
        Method to be overrriden by an instruction
        """
        print("MISSING EXEC METHOD")

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
        c = self.getV(self.cnd)
        if c:
            for i in self.t:
                i.exec()
        else:
            for i in self.f:
                i.exec()

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
        c = self.getV(self.cnd)
        while c:
            for i in self.t:
                i.exec()
            c = self.getV(self.cnd)

    def __str__(self):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        return f"WHILE ({self.cnd}) {{\n{t}\n}}"

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

    #def exec(self):
    #    ...

    def __str__(self):
        t = self.t
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        return f"FOR ({self.i} : {self.cnd}) {{\n{t}\n}}"
        
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
        s1 = self.getV(self.src1)
        s2 = self.getV(self.src2)
        self.check_types("*", s1, s2, {int, float})
        r = s1*s2
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
        s1 = self.getV(self.src1)
        s2 = self.getV(self.src2)
        self.check_types("+", s1, s2, {int, float, str, list})
        r = s1+s2
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
        s1 = self.getV(self.src1)
        s2 = self.getV(self.src2)
        self.check_types("-", s1, s2, {int, float})
        r = s1-s2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"SUB {self.src1}, {self.src2}, {self.dst}"
