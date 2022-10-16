import mash_exceptions as mex
from symbol_table import symb_table

def type_name(o):
    try:
        return o.type_name()
    except Exception:
        return o.__class__.__name__

class Value():
    """
    Values
    """
    def get_value(self):
        return self.value

    def __str__(self):
        return str(self.get_value())

    def type_name(self):
        return self.__class__.__name__

    def _at(self, index):
        raise mex.TypeError(f"Type {self.type_name} is not subscriptable")

    def _in(self, x):
        raise mex.TypeError(f"Type {self.type_name()} does not support operator 'in'")

    def _slice(self, i1, i2, step):
        raise mex.TypeError(f"Type {self.type_name} cannot be sliced")

    def __eq__(self, other):
        return self.get_value() == other.get_value()

    def fstr(self):
        return self.__str__()

class String(Value):
    """
    String
    """
    def __init__(self, value, escape_chs=True):
        self.original = value
        self.value = self.escape(value) if escape_chs else value

    def escape(self, value):
        return value.replace("\\n", "\n"
            ).replace("\\t", "\t"
            ).replace("\\", "\\"
            ).replace("\\\"", "\""
            ).replace("\\a", "\a"
            ).replace("\\b", "\b"
            ).replace("\\f", "\f"
            ).replace("\\r", "\r"
            ).replace("\\v", "\v")

    def __str__(self):
        return self.value

    def _at(self, index):
        if type(index) != Int:
            raise mex.TypeError("String index must be an Int")
        if index.get_value() >= len(self.value):
            raise mex.IndexError(f"Indxe {index.get_value()} is out of range for length {len(self.value)}")
        return String(self.value[index.get_value()])

    def _slice(self, i1, i2, step):
        i1 = i1 if i1 is not None else Int(0)
        i2 = i2 if i2 is not None else Int(len(self.value))
        step = step if step is not None else Int(1)
        if type(i1) != Int or type(i2) != Int or type(step) != Int:
            raise mex.TypeError("String slice indices must be Ints")
        if step.get_value() == 0:
            raise mex.ValueError("Slice step cannot be 0")
        return String(self.value[i1.get_value():i2.get_value():step.get_value()])

    def _in(self, x):
        return x.get_value() in self.value

    def __eq__(self, other):
        return self.value == other.value

    def fstr(self):
        return "\""+self.original+"\""

class RString(String):
    """
    Raw String
    """
    def __init__(self, value):
        super().__init__(value, False)

    def __str__(self):
        return self.value

class FString(String):
    """
    Formatted String
    """
    def __init__(self, value):
        mex.warning("FStrings are not yet implemented")
        super().__init__(value, False)

    def __str__(self):
        return self.value

class List(Value):
    """
    List
    """
    def __init__(self, value):
        self.value = value

    def _at(self, index):
        if type(index) != Int:
            raise mex.TypeError("List index must be an Int")
        if index.get_value() >= len(self.value):
            raise mex.IndexError(f"Indxe {index.get_value()} is out of range for length {len(self.value)}")
        return self.value[index.get_value()]

    def _slice(self, i1, i2, step):
        i1 = i1 if i1 is not None else Int(0)
        i2 = i2 if i2 is not None else Int(len(self.value))
        step = step if step is not None else Int(1)
        if type(i1) != Int or type(i2) != Int or type(step) != Int:
            raise mex.TypeError("String slice indices must be Ints")
        if step.get_value() == 0:
            raise mex.ValueError("Slice step cannot be 0")
        return String(self.value[i1.get_value():i2.get_value():step.get_value()])

    def _in(self, x):
        v = x.get_value() if type(x) != list else x
        for i in self.value:
            if type(i) == str:
                i = symb_table.get(i)
            a = i.get_value() if type(i) != list else i
            if a == v:
                return True
        return False

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        v = []
        for x in self.value:
            if type(x) == str:
                if(symb_table.analyzer):
                    v.append(x)
                else:
                    value = symb_table.get(x)
                    if type(value) == list:
                        v.append(value[0].fstr())
                    else:
                        v.append(value.fstr())
            else:
                v.append(x.fstr())
        return "["+", ".join(v)+"]"

class Dict(Value):
    """
    Dictionary
    """
    def __init__(self, value):
        self.value = value

    def _at(self, index):
        v = index.get_value() if type(index) != list else index
        for i, k in self.value:
            if type(i) == str:
                i = symb_table.get(i)
            a = i.get_value() if type(i) != list else i
            if a == v:
                return k
        return False

    def _in(self, x):
        v = x.get_value() if type(x) != list else x
        for i, _ in self.value:
            if type(i) == str:
                i = symb_table.get(i)
            a = i.get_value() if type(i) != list else i
            if a == v:
                return True
        return False

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        if len(self.value) == 0:
            return "{,}"
        v = []
        for x, y in self.value:
            if type(x) == str:
                if not symb_table.analyzer:
                    x = symb_table.get(x)
                    if type(x) == list:
                        x = x[0].fstr()
                    else:
                        x = x.fstr()
            else:
                x = x.fstr()
            if type(y) == str:
                if not symb_table.analyzer:
                    y = symb_table.get(y)
                    if type(y) == list:
                        y = y[0].fstr()
                    else:
                        y = y.fstr()
            else:
                y = y.fstr()
            v.append(x+": "+y)
        return "{"+", ".join(v)+"}"

class Float(Value):
    """
    Float
    """
    def __init__(self, value):
        self.value = value

class Int(Value):
    """
    Float
    """
    def __init__(self, value):
        self.value = value

class Bool(Value):
    """
    Boolean
    """
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def __str__(self):
        return "true" if self.value else "false"

class Nil(Value):
    """
    Nil
    """
    def __init__(self):
        self.value = None

    def get_value(self):
        return None

    def type_name(self):
        return "NilType"

    def __str__(self):
        return "nil"

    

IMPLICIT_TO_BOOL = {Int, Float, Nil}