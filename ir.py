from mash import Mash

class IR:
    """
    Base class for all ir nodes
    """

class Value(IR):
    """
    Values
    """

class NIL(Value):
    """
    Nil
    """
    def __str__(self):
        return "nil"

class TRUE(Value):
    """
    True
    """
    def __str__(self):
        return "true"

class FALSE(Value):
    """
    False
    """
    def __str__(self):
        return "false"

class AssignVar(IR):
    """
    Variable declaration and definition
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"SET {self.name}, {self.value}"

class Print(IR):
    """
    Variable declaration and definition
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"PRINT {self.value}"

class ToString(IR):
    """
    Convert value to a string
    """
    def __init__(self, dst, value):
        self.dst = dst
        self.value = value

    def __str__(self):
        return f"TOSTR {self.dst}, {self.value}"

class Nop(IR):
    """
    No operation
    """
    def __init__(self):
        pass

    def __str__(self):
        return "NOP"

class If(IR):
    """
    If statement
    """
    def __init__(self, cnd, t, f):
        self.cnd = cnd
        self.t = t
        self.f = f

    def __str__(self):
        t = self.t
        f = self.f
        if type(self.t) == list:
            t = "\n".join(str(i) for i in t)
        if type(self.f) == list:
            f = "\n".join(str(i) for i in f)
        return f"IF ({self.cnd}) {{\n{t}\n}} ELSE {{\n{f}}}"
        
class Expr(IR):
    """
    """

class Mul(Expr):
    """
    Multiplication
    """
    def __init__(self, dst, src1, src2):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def __str__(self):
        return f"MUL {self.dst}, {self.src1}, {self.src2}"