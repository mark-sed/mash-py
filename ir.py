from symbol_table import symb_table
from mash import Mash
import mash_exceptions as mex

class IR:
    """
    Base class for all ir nodes
    """

class Value(IR):
    """
    Values
    """
    def get_value(self):
        raise mex.Unimplemented()

class STRING(Value, str):
    """
    String
    """
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def __str__(self):
        return super(str).__str__()

class NIL(Value):
    """
    Nil
    """
    def get_value(self):
        return None

    def __str__(self):
        return "nil"

class TRUE(Value):
    """
    True
    """
    def get_value(self):
        return True

    def __str__(self):
        return "true"

class FALSE(Value):
    """
    False
    """
    def get_value(self):
        return False

    def __str__(self):
        return "false"

class Instruction(IR):
    """
    Base class for all instructions
    """

    def exec(self):
        """
        Method to be overrriden by an instruction
        """
        print("MISSING EXEC METHOD")

    def getV(self, name):
        if type(name) == str:
            return symb_table.get(name)
        elif isinstance(type(name), Value):
            return name.get_value()

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
    def __init__(self, value, dst=NIL()):
        self.dst = dst
        self.value = value

    def exec(self):
        print(self.getV(self.value), end="")

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
        symb_table.assign(self.dst, str(self.getV(self.value)))

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
    def vsrc1(self):
        if type(self.src1) == str:
            return symb_table.get(self.src1)
        else:
            return self.src1

    def vsrc2(self):
        if type(self.src2) == str:
            return symb_table.get(self.src2)
        else:
            return self.src2

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
        s1 = self.vsrc1()
        s2 = self.vsrc2()
        self.check_types("*", s1, s2, {int, float})
        symb_table.assign(self.dst, s1*s2)

    def __str__(self):
        return f"MUL {self.src1}, {self.src2}, {self.dst}"
