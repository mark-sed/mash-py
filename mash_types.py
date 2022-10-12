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

    def __str__(self):
        v = []
        for x in self.value:
            if type(x) == str:
                if(symb_table.analyzer):
                    v.append(x)
                else:
                    v.append(symb_table.get(x).fstr())
            else:
                v.append(x.fstr())
        return "["+", ".join(v)+"]"

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