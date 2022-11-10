"""
Internal implementation for libmash functions
@version: 0.0.1
"""
from copy import copy
import random
import math

import mash_types as types
import mash_exceptions as mex
from symbol_table import symb_table, ClassFrame, SpaceFrame

def Int_Int_2(self, v):
    if type(v) == int:
        return v
    if type(v) == str:
        return int(v, base=0)
    if type(v) == types.Class:
        v.call_method("__Int", [])
        return types.Var(symb_table.RETURN_NAME)
    try:
        return int(v)
    except ValueError:
        raise mex.ValueError(f"Cannot convert '{v}' to Int")

def Float_Float_2(self, v):
    if type(v) == float:
        return v
    if type(v) == types.Class:
        v.call_method("__Float", [])
        return types.Var(symb_table.RETURN_NAME)
    try:
        return float(v)
    except ValueError:
        raise mex.ValueError(f"Cannot convert '{v}' to Float")

def String_String_2(self, v):
    if type(v) in {int, float, str, bool}:
        return str(v)
    if type(v) == list:
        return types.List(v).fstr()
    if type(v) == tuple:
        return types.Dict(v).fstr()
    if type(v) == types.Class:
        v.call_method("__String", [])
        return types.Var(symb_table.RETURN_NAME)
    if v is None:
        return types.Nil().fstr()
    raise mex.Unimplemented("Calls to '_to' function is not yet implemented")

def Bool_Bool_2(self, v):
    if type(v) == bool:
        return v
    if type(v) == types.Class:
        v.call_method("__Bool", [])
        return types.Var(symb_table.RETURN_NAME)
    try:
        return bool(v)
    except ValueError:
        raise mex.ValueError(f"Cannot convert '{v}' to Bool")

def List_List_1(self):
    return []

def List_List_3(self, a, b):
    return types.List([types.wrap_py(a)]+b)

def Dict_Dict_1(self):
    return types.Dict()

def NilType_NilType_1(self):
    return None

def type_1(var):
    ir_type = types.wrap_py(var)
    if type(ir_type) in {ClassFrame, SpaceFrame, types.Enum}:
        return symb_table.get("Type")
    if type(ir_type) == types.Class:
        ir_type = ir_type.frame
    e, _ = symb_table.exists(ir_type.type_name())
    if e:
        return symb_table.get(ir_type.type_name())
    raise mex.Unimplemented("Type value for given type")

def id_1(var):
    return id(var)

def vardump_1(var):
    r = []
    for v in var:
        r.append(types.vardump(v))
    return "\n".join(r)

def getattr_3(object, name, default):
    if type(name) != str:
        raise mex.TypeError("Attribute name has to be a String")
    if type(object) == types.Class:
        if name in object.attr:
            a = object.attr[name]
            if type(a) == list:
                return types.Var([object.name, "::", a[0].name])
            return a
        else:
            if type(default) != types.NoValue:
                return default
            raise mex.UndefinedReference("'"+name+"' in instance of class '"+object.name+"'")
    elif type(object) == types.ClassFrame:
        if name in object:
            a = object[name]
            if type(a) == list:
                return types.Var([object.name, "::", a[0].name])
            return a
        else:
            if type(default) != types.NoValue:
                return default
            raise mex.UndefinedReference("'"+name+"' in class '"+object.name+"'")
    elif type(object) == types.SpaceFrame:
        if name in object:
            a = object[name]
            if type(a) == list:
                return types.Var([object.name, "::", a[0].name])
            return a
        else:
            if type(default) != types.NoValue:
                return default
            raise mex.UndefinedReference("'"+name+"' in space '"+object.name+"'")
    raise mex.UndefinedReference(name)

def getattr_2(object, name):
    return getattr_3(object, name, types.NoValue)

def setattr_3(object, name, value):
    if type(name) != str:
        raise mex.TypeError("Attribute name has to be a String")

    if type(object) == types.Class:
        object.attr[name] = types.wrap_py(value)
    elif type(object) == types.ClassFrame or type(object) == types.SpaceFrame:
        symb_table.assign(["@", object.name, "::", name], types.wrap_py(value))
    else:
        raise mex.TypeError("Cannot set attribute for given type")

def bitand_2(a, b):
    return a & b

def bitor_2(a, b):
    return a | b

def bitxor_2(a, b):
    return a ^ b

def bitnot_1(a):
    return ~a

def lshift_2(a, count):
    return a << count

def rshift_2(a, count):
    return a >> count

def zip_2(l1, l2):
    return [types.List([a, b]) for a, b in zip(l1, l2)]

def shuffle_1(l):
    retv = copy(l)
    random.shuffle(retv)
    return retv

def reverse_1(l):
    retv = copy(l)
    retv.reverse()
    return retv

def cos_1(x):
    return math.cos(x)

def sin_1(x):
    return math.sin(x)

def tan_1(x):
    return math.tan(x)

def acos_1(x):
    return math.acos(x)

def asin_1(x):
    return math.asin(x)

def atan_1(x):
    return math.atan(x)

def atan_2(y, x):
    return math.atan2(y, x)

def upper_1(x):
    if type(x) != str:
        raise mex.TypeError("toupper accepts only String")
    return x.upper()

def lower_1(x):
    if type(x) != str:
        raise mex.TypeError("tolower accepts only String")
    return x.lower()

def capitalize_1(x):
    if type(x) != str:
        raise mex.TypeError("capitalize accepts only String")
    return x.capitalize()