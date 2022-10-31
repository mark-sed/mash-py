import mash_exceptions as mex

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

    def update(self):
        ...

    def _at(self, index):
        raise mex.TypeError(f"Type {self.type_name()} is not subscriptable")

    def _in(self, x):
        raise mex.TypeError(f"Type {self.type_name()} does not support operator 'in'")

    def _slice(self, i1, i2, step):
        raise mex.TypeError(f"Type {self.type_name()} cannot be sliced")

    def __eq__(self, other):
        return self.get_value() == other.get_value()

    def ir_str(self):
        return f"{self.type_name()}({self.fstr()})"

    def fstr(self):
        return self.__str__()

class VarArgs:
    ...

class Class(Value):
    """
    Class type
    """
    def __init__(self, name, frame):
        self.value = name
        self.name = name
        self.frame = frame
        self.attr = {}
        for v, k in self.frame.items():
            if type(v) == list:
                self.attr[k] = v

    def __contains__(self, key):
        return self.attr.__contains__(key)

    def __getitem__(self, key):
        return self.attr[key]

    def __setitem__(self, key, value):
        return self.attr.__setitem__(key, value)

    def __delitem__(self, key):
        self.attr.__delitem__(key)

    def __iter__(self):
        return self.attr.__iter__()
    
    def __len__(self):
        return self.attr.__len__()

    def __str__(self):
        n = "".join(self.value)
        return f"<{n} object>"

from symbol_table import symb_table

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
            if type(i) == str or type(i) == list:
                i = symb_table.get(i)
            a = i.get_value() if type(i) != list else i
            if a == v:
                return True
        return False

    def update(self):
        for c, x in enumerate(self.value):
            if type(x) == str or type(x) == list:
                self.value[c] = symb_table.get(x)
            else:
                x.update()

    def __eq__(self, other):
        return self.value == other.value

    def fstr(self):
        return str(self)

    def __str__(self):
        v = []
        for x in self.value:
            if type(x) == str or type(x) == list:
                if(symb_table.analyzer):
                    if type(x) == list:
                        v.append("".join(x))
                    else:
                        v.append(x)
                else:
                    if type(x) == list:
                        # Fun
                        if len(x) > 0 and type(x[0]) != str:
                            v.append(x[0].fstr())
                            continue
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
        raise mex.KeyError(str(index))

    def _in(self, x):
        v = x.get_value() if type(x) != list else x
        for i, _ in self.value:
            if type(i) == str or type(i) == list:
                i = symb_table.get(i)
            a = i.get_value() if type(i) != list else i
            if a == v:
                return True
        return False

    def __eq__(self, other):
        return self.value == other.value

    def items(self):
        return List([List([x, y]) for x, y in self.value])

    def update(self):
        for c, i in enumerate(self.value):
            k, v = i
            if type(k) == str or type(k) == list:
                k = symb_table.get(k)
            else:
                k.update()
            if type(v) == str or type(v) == list:
                v = symb_table.get(v)
            else:
                v.update()
            self.value[c] = (k, v)

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
            if type(y) == str or type(y) == list:
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