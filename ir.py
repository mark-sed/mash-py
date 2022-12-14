from typing import Type
from symbol_table import symb_table, SymbTable, ClassFrame, Frame, SpaceFrame
import mash_exceptions as mex
from mash_types import Float, Int, Nil, Bool, String, Value, List, Dict, VarArgs
import mash_types as types
import libmash

output_print = []

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
            raise mex.Unimplemented(f"Getter for IR node type ({name})")

    def output(self, indent=0):
        return (indent*IR.SPCS)+str(self)

def wrap(v):
    if type(v) == types.Var:
        return v.name
    elif type(v) == int:
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
        self.skip = False
        if type(self.dst) == list and type(self.dst[0]) != str:
            self.skip = True
        if type(self.value) == list and type(self.value[0]) != str:
            self.skip = True
        if (type(self.value) != str or type(self.value) != list) and self.dst == self.value:
            self.skip = True

    def exec(self):
        if self.skip:
            return
        self.update(self.value)
        symb_table.assign(self.dst, self.value)

    def __str__(self):
        if self.skip:
            return "NOP"
        return f"SET {ir_str(self.value)}, {ir_str(self.dst)}"

class AssignMultiple(Instruction):
    """
    Multiple variable assignment
    """
    def __init__(self, dst, value):
        self.dst = dst
        self.value = value
        if issubclass(type(value), Type) and type(value) != List:
            raise mex.TypeError(f"Cannot unpack type {value.type_name()}")

    def exec(self):
        self.update(self.value)
        v = self.get(self.value)
        if type(v) != List:
            raise mex.TypeError(f"Cannot unpack type {v.type_name()}")
        if len(self.dst) > len(v.get_value()):
            raise mex.TypeError(f"Not enough values to unpack. Expected {len(self.dst)}, but got {len(v.get_value())}")
        # Remove is unpacking of multiple to last one is allowed
        if len(self.dst) < len(v.get_value()):
            raise mex.TypeError(f"Too many values to unpack. Expected {len(self.dst)}, but got {len(v.get_value())}")
        for c, d in enumerate(self.dst):
            if c == len(self.dst)-1 and c < len(v.get_value())-1:
                symb_table.assign(d, List(v.get_value()[c:]))
            else:
                symb_table.assign(d, v.get_value()[c])

    def __str__(self):
        dst_str = ["".join(x) for x in self.dst]
        return f"MSET {ir_str(self.value)}, {dst_str}"

class Print(Instruction):
    """
    Variable declaration and definition
    """
    def __init__(self, value, output_file=None, output_format=None):
        self.value = value
        self.output_file = output_file
        self.output_format = output_format

    def exec(self):
        self.update(self.value)
        v = self.get(self.value)
        if type(v) == list:
            # Function/s (there can be multiple)
            details = ""
            if len(v) > 1:
                details = f" with {len(v)} signatures"
            n = "".join(v[0].name)
            # Function/s (there can be multiple)
            t = f"<function '{n}'{details}>"
        else:
            t = v.__str__()
        print(t, end="")
        output_print.append(t)

    def __str__(self):
        return f"PRINT {ir_str(self.value)}"

class Note(Instruction):
    """
    Notebook note
    """
    def __init__(self, value, output_file, output_format, output_notes):
        self.output_file = output_file
        self.output_format = output_format
        self.output_notes = output_notes
        self.value = value

    def exec(self):
        if self.output_notes:
            print(self.value)
        if self.output_file is not None:
            with open(self.output_file, "a", encoding="utf-8") as outf:
                outf.write(self.value.get_value())

    def __str__(self):
        #show = 15
        #if len(self.value.get_value()) > show:
        #    return f"NOTE \"\"\"{self.value.get_value()[:show]}..."
        #else:
        return f"NOTE \"\"\"{self.value}\"\"\""

class Doc(Instruction):
    """
    Documentation for an object
    """
    def __init__(self, value):
        self.value = value
        self.dst = None

    def exec(self):
        if self.dst is None:
            self.dst = symb_table.last_exec
        if type(self.dst) in {Fun, SpaceFrame, ClassFrame}:
            self.dst.doc = self.value

    def __str__(self):
        #show = 15
        #if len(self.value.get_value()) > show:
        #    return f"DOC \"\"\"{self.value.get_value()[:show]}..."
        #else:
        if self.dst is not None:
            return f"DOC \"\"\"{self.value}\"\"\", {ir_str(self.dst)}"
        else:
            return f"DOC \"\"\"{self.value}\"\"\""

class SetIfNotSet(Instruction):
    """
    If variable is not yet set, then this declares it,
    if it is set, then it prints it
    """
    def __init__(self, dst, value=Nil()):
        self.dst = dst
        self.value = value

    def exec(self):
        self.update(self.value)
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
    def __init__(self, dst, value=Nil(), output_file=None, output_format=None):
        self.dst = dst
        self.value = value
        self.output_file = output_file
        self.output_format = output_format

    def exec(self):
        self.update(self.value)
        s, _ = symb_table.exists(self.dst)
        if not s:
            self.update(self.value)
            symb_table.assign(self.dst, self.value)
        else:
            self.update(self.dst)
            v = self.get(self.dst)
            if type(v) == list:
                details = ""
                if len(v) > 1:
                    details = f" with {len(v)} signatures"
                n = "".join(v[0].name)
                # Function/s (there can be multiple)
                t = f"<function '{n}'{details}>"
            else:
                t = v.__str__()
            print(t, end="")
            output_print.append(t)

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

#class ListWrap(Instruction):
#    """
#    Wrap value as a list
#    """
#    def __init__(self, value, dst):
#        self.dst = dst
#        self.value = value
#
#    def exec(self):
#        v = self.get(self.value)
#        symb_table.assign(self.dst, List([v]))
#
#    def __str__(self):
#        return f"LISTWRAP {ir_str(self.value)}, {self.dst}"

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
        #if cnd != str and cnd != list and (type(cnd) not in types.IMPLICIT_TO_BOOL):
        #    raise mex.TypeError("Unexpected expression type in if statement condition")
        self.t = t
        if type(self.t) is not list:
            self.t = [self.t]
        self.f = f
        if type(self.f) is not list:
            self.f = [self.f]

    def exec(self):
        symb_table.push()
        c = self.get(self.cnd)
        if type(c) == types.Class:
            raise mex.Unimplemented("Call to _to method")
        elif type(c) != Bool and type(c) not in types.IMPLICIT_TO_BOOL:
            raise mex.TypeError(f"Unexpected expression type '{c.type_name()}' in if statement condition")
        else:
            c = c.get_value()
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
        c = self.get(self.cnd)
        if type(c) == types.Class:
            raise mex.Unimplemented("Call to _to method")
        elif type(c) != Bool and type(c) not in types.IMPLICIT_TO_BOOL:
            raise mex.TypeError(f"Unexpected expression type '{c.type_name()}' in while statement condition")
        else:
            c = c.get_value()
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
        c = self.get(self.cnd)
        if type(c) == types.Class:
            raise mex.Unimplemented("Call to _to method")
        elif type(c) != Bool and type(c) not in types.IMPLICIT_TO_BOOL:
            raise mex.TypeError(f"Unexpected expression type '{c.type_name()}' in do while statement condition")
        else:
            c = c.get_value()
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
            c = self.get(self.cnd)
            if type(c) == types.Class:
                raise mex.Unimplemented("Call to _to method")
            elif type(c) != Bool and type(c) not in types.IMPLICIT_TO_BOOL:
                raise mex.TypeError(f"Unexpected expression type '{c.type_name()}' in do while statement condition")
            else:
                c = c.get_value()
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
        if type(s) != List and type(s) != Dict and type(s) != types.Class:
            raise mex.TypeError(f"Cannot iterate over {s.type_name()}")
        v = s.get_value()
        if type(s) == Dict:
            v = s.items().get_value()
        
        if type(s) == types.Class:
            if type(self.l) == list:
                l += [".", "__next"]
            else:
                l = [self.l, ".", "__next"]
            
            next_call = FunCall(l, [])
            next_call.exec()
            a = symb_table.get(SymbTable.RETURN_NAME)
            if not (type(a) == types.ClassFrame and a.name == "StopIteration"):
                if len(self.i) > 1:
                    if type(a) != List:
                        raise mex.TypeError(f"Cannot unpack type {a.type_name()}")
                    if len(self.i) > len(a.get_value()):
                        raise mex.TypeError(f"Not enough values to unpack. Expected {len(self.i)}, but got {len(a.get_value())}")
                    # Remove is unpacking of multiple to last one is allowed
                    if len(self.i) < len(a.get_value()):
                        raise mex.TypeError(f"Too many values to unpack. Expected {len(self.i)}, but got {len(a.get_value())}")
                    for c, i_name in enumerate(self.i):
                        if c == len(self.i)-1 and c < len(a.get_value())-1:
                            symb_table.assign(i_name, List(a.get_value()[c:]))
                        else:
                            symb_table.assign(i_name, a.get_value()[c])
                else:
                    self.i = self.i[0]
                    symb_table.assign(self.i, a)
            while not (type(a) == types.ClassFrame and a.name == "StopIteration"):
                try:
                    for i in self.t:
                        i.exec()
                    next_call.exec()
                    a = symb_table.get(SymbTable.RETURN_NAME)
                    if not (type(a) == types.ClassFrame and a.name == "StopIteration"):
                        if len(self.i) > 1:
                            if type(a) != List:
                                raise mex.TypeError(f"Cannot unpack type {a.type_name()}")
                            if len(self.i) > len(a.get_value()):
                                raise mex.TypeError(f"Not enough values to unpack. Expected {len(self.i)}, but got {len(a.get_value())}")
                            # Remove is unpacking of multiple to last one is allowed
                            if len(self.i) < len(a.get_value()):
                                raise mex.TypeError(f"Too many values to unpack. Expected {len(self.i)}, but got {len(a.get_value())}")
                            for c, i_name in enumerate(self.i):
                                if c == len(self.i)-1 and c < len(a.get_value())-1:
                                    symb_table.assign(i_name, List(a.get_value()[c:]))
                                else:
                                    symb_table.assign(i_name, a.get_value()[c])
                        else:
                            self.i = self.i[0]
                            symb_table.assign(self.i, a)
                    else:
                        break
                except mex.FlowControlBreak:
                    break
                except mex.FlowControlContinue:
                    continue
                except mex.FlowControlReturn as e:
                    symb_table.pop()
                    raise e
        else:
            for a in v:
                if len(self.i) > 1:
                    if type(a) != List:
                        raise mex.TypeError(f"Cannot unpack type {a.type_name()}")
                    if len(self.i) > len(a.get_value()):
                        raise mex.TypeError(f"Not enough values to unpack. Expected {len(self.i)}, but got {len(a.get_value())}")
                    # Remove is unpacking of multiple to last one is allowed
                    if len(self.i) < len(a.get_value()):
                        raise mex.TypeError(f"Too many values to unpack. Expected {len(self.i)}, but got {len(a.get_value())}")
                    for c, i_name in enumerate(self.i):
                        if c == len(self.i)-1 and c < len(a.get_value())-1:
                            symb_table.assign(i_name, List(a.get_value()[c:]))
                        else:
                            symb_table.assign(i_name, a.get_value()[c])
                else:
                    symb_table.assign(self.i[0], a)
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
        self.doc = String("")
        if len(self.args) > 0 and type(self.args[-1][1]) == types.VarArgs:
            self.max_args = float("inf")
        self.body = body
        self.internal = False
        self.method = type(symb_table.top()) == ClassFrame
        if not self.method and self.name[0] == "(":
            raise mex.TypeError("Operator overloading is only possible for class methods, not functions")
        if len(self.body) > 0 and type(self.body[0]) == Internal:
            self.internal = True
            try:
                if self.method:
                    self.body = getattr(libmash, symb_table.top().name+"_"+name+"_"+str(len(args)))
                else:
                    self.body = getattr(libmash, name+"_"+str(len(args)))
            except AttributeError:
                raise mex.UndefinedReference(self.str_header())

    def exec(self):
        # Exec is for definition
        if type(self.body) == list:
            for i in self.body:
                if type(i) == Doc:
                    i.dst = self
                    self.doc = i.value
        symb_table.define_fun(self.name, self.min_args, self.max_args, self)

    def wrap_internal(self, v):
        """
        Wraps value returned by internal function into IR value if not yet wrapped
        """
        if   type(v) == types.Var: return v.name
        elif type(v) == int: return types.Int(v)
        elif type(v) == float: return types.Float(v)
        elif type(v) == str: return types.String(v)
        elif type(v) == list: return types.List(v)
        elif type(v) == tuple: return types.Dict(v)
        elif type(v) == bool: return types.Bool(v)
        elif v is None: return types.Nil()
        else: return v

    def call(self):
        if self.internal:
            assign_args = []
            for a, _ in self.args:
                if type(a) == tuple:
                    a = a[0]
                v = symb_table.get(a)
                if type(v) != list:
                    assign_args.append(v.get_value())
                else:
                    assign_args.append(v)
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
                if type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]}")
                else:
                    args.append(str(k))
            else:
                if type(v) == VarArgs:
                    args.append(f"*{k}")
                elif type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]} = {str(v)}")
                else:
                    args.append(f"{k} = {str(v)}")
        args_s = ", ".join(args)
        return f"fun {self.name}({args_s})"+(" internal" if self.internal else "")

    def fstr(self):
        #details = ""
        #v = symb_table.get(self.name)
        #if len(v) > 1:
        #    details = f" with {len(v)} signatures"
        n = "".join(self.name)
        return f"<function '{n}'>"

    def ir_str(self):
        return self.fstr()

    def output(self, indent=0):
        if self.internal:
            return self.str_header()
        t = self.body
        if type(self.body) == list:
            t = "\n".join(i.output(indent+1) for i in t)
        args = []
        for k, v in self.args:
            if v is None:
                if type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]}")
                else:
                    args.append(str(k))
            else:
                if type(v) == VarArgs:
                    args.append(f"*{k}")
                elif type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]} = {str(v)}")
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
                if type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]}")
                else:
                    args.append(str(k))
            else:
                if type(v) == VarArgs:
                    args.append(f"*{k}")
                elif type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]} = {str(v)}")
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
        if len(symb_table.spaces) == 0:
            raise mex.IncorrectDefinition("Constructor has to be inside of a class")
        parent_class_name = symb_table.spaces[-1].name
        if name != parent_class_name:
            raise mex.IncorrectDefinition("Constructor name has to match the class name")
        if len(args) < 1:
            raise mex.TypeError("Constructor has to take at least one argument - the object itself")
        super(Constructor, self).__init__(name, args, body)

    def call(self):
        if self.internal:
            assign_args = []
            for a, _ in self.args:
                if type(a) == tuple:
                    a = a[0]
                v = symb_table.get(a)
                if type(v) == list:
                    assign_args.append(v)
                else:
                    assign_args.append(v.get_value())
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
                    if type(r.value) != Nil:
                        raise mex.TypeError("Constructor has to return nil")
                    return r.value, r.frames
            if type(self.args[0][1]) == types.VarArgs:
                return symb_table.get(self.args[0][0]).get_value()[0], 1
            return symb_table.get(self.args[0][0]), 1

    def str_header(self):
        args = []
        for k, v in self.args:
            if v is None:
                if type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]}")
                else:
                    args.append(str(k))
            else:
                if type(v) == VarArgs:
                    args.append(f"*{k}")
                elif type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]} = {str(v)}")
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
                if type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]}")
                else:
                    args.append(str(k))
            else:
                if type(v) == VarArgs:
                    args.append(f"*{k}")
                elif type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]} = {str(v)}")
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
                if type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]}")
                else:
                    args.append(str(k))
            else:
                if type(v) == VarArgs:
                    args.append(f"*{k}")
                elif type(k) == tuple:
                    args.append(f"{k[0]}:{k[1]} = {str(v)}")
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
        if type(name) == list and issubclass(type(name[0]), Value):
            v = name[0]
            self.name = [v.type_name(), "::"]+name[2:]
            self.args = [v]+args
        else:
            self.name = name
            self.args = args
        self.dst = SymbTable.RETURN_NAME
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
        const_call = False
        if type(self.name) == list and len(self.name) > 2 and self.name[-2] == ".":
            method_call = True
            # Firsts check object attributes
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
                if type(frame[-1]) == dict: # attr
                    method_call = False
                    frame = frame[-1]
                elif type(frame[-1]) == tuple:
                    self.args = [frame[-1][0]]+self.args
                    frame = frame[-1][0].access(frame[-1][1]) 
                    const_call = True
                else:
                    if type(frame) == types.Class:
                        frame = frame[-1].frame
                    else:
                        frame = None
        else:
            frame = symb_table.get_frame(self.name)

        if frame is None:
            fl = None
        else:
            if type(self.name) == list:
                n = self.name[-1]
            else:
                n = self.name
            if const_call:
                fl = frame
            else:
                try:
                    fl = frame[n]
                except KeyError:
                    raise mex.UndefinedReference("".join(self.name))
        if fl is None:
            raise mex.UndefinedReference("".join(self.name))
        if type(fl) != list and type(fl) != ClassFrame:
            if self.name[0] == "'":
                raise mex.TypeError("Type '"+types.type_name(fl)+"' is not callable")
            else:
                raise mex.TypeError("'"+"".join(self.name)+"' is not callable")
        f = []
        new_obj = False
        if type(fl) == ClassFrame:
            new_obj = True
            n = fl.name
            if n not in fl:
                symb_table.assign(SymbTable.RETURN_NAME, fl.instance())
                return
            else:
                for i in fl[n]:
                    # Find matching function signature
                    if i.max_args-1 >= len(self.args):
                        f.append(i)
                if len(f) == 0:
                    raise mex.UndefinedReference(f"Arguments do not match any class '{self.name}' constructors")
        else:
            for i in fl:
                # Find closest matching function signature
                if i.max_args >= len(self.args):
                    f.append(i)
            if len(f) == 0:
                if self.name[0] == "'":
                    raise mex.UndefinedReference(f"Arguments do not match any function's '{fl[0].name}' signatures")
                else:
                    raise mex.UndefinedReference(str(self))
            else:
                for fi in f:
                    if type(fi) == Constructor:
                        raise mex.TypeError("Constructor cannot be called as a function")
        # Recheck if function was assigned to the object or if it is the class method
        if not method_call and len(f) > 0:
            method_call = f[0].method
        assigned = []
        start_arg_i = 0
        if new_obj:
            if len(f[0].args) == 0:
                raise mex.TypeError("Class methods have to take the object as its first attribute")
            if type(f[0].args[0][0]) == tuple:
                raise mex.TypeError("Object argument (self) cannot be type constrained")
            if type(f[0].args[0][1]) == types.VarArgs:
                assigned = [(f[0].args[0][0], types.List([fl.instance()]+self.pos_args))]
            else:
                assigned = [(f[0].args[0][0], fl.instance())]
            start_arg_i = 1
        elif method_call:
            if len(f[0].args) == 0:
                raise mex.TypeError("Class methods have to take the object as its first attribute")
            if type(f[0].args[0][0]) == tuple:
                raise mex.TypeError("Object argument (self) cannot be type constrained")
            if type(f[0].args[0][1]) == types.VarArgs:
                assigned = [(f[0].args[0][0], types.List([self.name[-3]]+self.pos_args))]
            else:
                assigned = [(f[0].args[0][0], self.name[-3])]
            start_arg_i = 1

        f_match = None
        f_excp = None
        assign_rest = []
        f.sort(key=lambda x: sum([1 if type(a[0]) == tuple else 0 for a in x.args]), reverse=True)
        for f_adept in f:
            assign_rest = []
            found = True
            f_match = f_adept
            for i, a in enumerate(f_adept.args[start_arg_i:]):
                v = a[1]
                a = a[0]
                a_str = str(a) if type(a) != tuple else str(a[0])
                if type(v) == types.VarArgs:
                    value = types.List(self.pos_args[i:])
                    # Update in case of variable names
                    value.update()
                else:
                    if i >= len(self.pos_args):
                        if v is None:
                            f_excp = mex.TypeError(f"Function call to '{f_adept.str_header()}' is missing required positional argument '{a_str}'")
                            found = False
                            break
                        else:
                            break
                    passed = self.pos_args[i]
                    value = passed
                    if type(passed) == str or type(passed) == list: 
                        # Variable
                        value = symb_table.get(passed)
                    if type(a) == tuple:
                        for t in a[1]:
                            if t == value.type_name():
                                break
                        else:
                            found = False
                            supp_t = ", ".join(a[1])
                            f_excp = mex.TypeError(f"Passed in value for argument {a_str} has unexpected type ({value.type_name()}). Value should be of following type: {supp_t}")
                if type(a) == tuple:
                    assign_rest.append((a[0], value))
                else:
                    assign_rest.append((a, value))
            if found:
                break

        if not found:
            raise f_excp
        assigned += assign_rest

        for k, v in self.named_args:
            for a, b in f_match.args:
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
        for k, v in f_match.args:
            if v is not None:
                if type(k) == tuple:
                    k = k[0]
                symb_table.assign(k, v)
        for k, v in assigned:
            symb_table.assign(k, v)
        ret_val, frames = f_match.call()
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
        if type(v) == types.Var:
            symb_table.assign(self.dst, v.name)
        else:
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
        i1 = self.i1 if self.i1 is None else self.get(self.i1)
        i2 = self.i2 if self.i2 is None else self.get(self.i2)
        step = self.step if self.step is None else self.get(self.step)
        v = s1._slice(i1, i2, step)
        if type(v) == types.Var:
            symb_table.assign(self.dst, v.name)
        else:
            symb_table.assign(self.dst, v)

    def __str__(self):
        end_str = types.Nil() if self.i2 is None else ir_str(self.i2)
        start_str = types.Nil() if self.i1 is None else ir_str(self.i1)
        step_str = types.Nil() if self.step is None else ir_str(self.step)
        return f"SLICE {ir_str(self.src)}, {start_str}, {end_str}, {step_str}, {self.dst}"

class SpacePush(Instruction):
    """
    Starts namespace
    """
    def __init__(self, name):
        self.name = name
        self.doc = String("")

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
    def __init__(self, name, extends):
        self.name = name
        self.extends = extends
        self.doc = String("")

    def exec(self):
        symb_table.push_class(self.name, self.extends)

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
        v = self.get(self.value)
        v.update()
        raise mex.FlowControlReturn(v)

    def __str__(self):
        return "return "+str(self.value)
        
class Expr(IR):
    """
    Expression
    """
    def check_types(self, op, s1, s2, allowed):
        if type(s1) == list:
            s1 = s1[0]
        if type(s2) == list:
            s2 = s2[0]
        if (type(s1) == str or type(s2) == str) or not ((type(s1) in allowed) and (type(s2) in allowed)):
            raise mex.TypeError(f"Unsupported types for '{op}'. Given values are '{s1}' and '{s2}'")

    def check_type(self, op, s, allowed):
        if type(s) == list:
            s = s[0]
        if type(s) == str or (type(s) not in allowed):
            raise mex.TypeError(f"Unsupported type for '{op}'. Given value is '{s}'")

    def class_call(self, fname, s1, s2):
        if type(s1) == types.Class:
            s1.call_method(fname, [s2])
            return types.Var(SymbTable.RETURN_NAME)
        return None

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
        r = self.class_call("(*)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(+)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
            try:
                self.check_types("+", s1, s2, {Int, Float})
            except mex.TypeError:
                try:
                    self.check_types("+", s1, s2, {String})
                except mex.TypeError:
                    self.check_types("+", s1, s2, {List})
            s1.update()
            s2.update()
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
        r = self.class_call("(-)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(/)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(//)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(%)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(^)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
            self.check_types("^", s1, s2, {Int, Float})
            v1 = s1.get_value()
            v2 = s2.get_value()
            r = v1 ** v2
            symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"EXP {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Cat(Expr):
    """
    Concatenation
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        if type(s1) == list:
            v1 = s1[0].fstr()
        else:
            v1 = s1.__str__()
            if type(v1) == types.String:
                v1 = v1.get_value()
            elif type(v1) != str:
                raise mex.TypeError(f"Attribute of ++ has incorrect type. String is expected, but got {v1.type_name()}")

        if type(s2) == list:
            v2 = s2[0].fstr()
        else:
            v2 = s2.__str__()
            if type(v2) == types.String:
                v2 = v2.get_value()
            elif type(v2) != str:
                raise mex.TypeError(f"Attribute of ++ has incorrect type. String is expected, but got {v2.type_name()}")
        
        r = v1+v2
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"CAT {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

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
        if type(r) == types.Var:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(or)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        return f"LOR {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

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
        r = self.class_call("(and)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        return f"LAND {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Or(Expr):
    """
    Shortcircuit OR
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        r = self.class_call("(||)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
            if type(s1) in types.IMPLICIT_TO_BOOL:
                v1 = bool(v1.get_value())
                s1 = types.Bool(v1)
            else:
                v1 = s1.get_value()
            self.check_type("short-circuit or", s1, {Bool})

            if v1:
                symb_table.assign(self.dst, wrap(v1))
            else:
                v2 = s2.get_value()
                symb_table.assign(self.dst, wrap(v2))

    def __str__(self):
        return f"OR {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class And(Expr):
    """
    Shortcircuit AND
    """
    def __init__(self, src1, src2, dst):
        self.dst = dst
        self.src1 = src1
        self.src2 = src2

    def exec(self):
        s1 = self.get(self.src1)
        s2 = self.get(self.src2)
        r = self.class_call("(&&)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
            if type(s1) in types.IMPLICIT_TO_BOOL:
                v1 = bool(v1.get_value())
                s1 = types.Bool(v1)
            else:
                v1 = s1.get_value()
            self.check_type("short-circuit and", s1, {Bool})

            if not v1:
                symb_table.assign(self.dst, wrap(v1))
            else:
                v2 = s2.get_value()
                symb_table.assign(self.dst, wrap(v2))

    def __str__(self):
        return f"AND {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class LNot(Expr):
    
    def __init__(self, src1, dst):
        self.dst = dst
        self.src1 = src1

    def exec(self):
        s1 = self.get(self.src1)
        if type(s1) == types.Class:
            s1.call_method("(!)", [])
            symb_table.assign(self.dst, SymbTable.RETURN_NAME)
        else:
            if type(s1) in types.IMPLICIT_TO_BOOL:
                v1 = bool(s1.get_value())
                s1 = types.Bool(v1)
            else:
                v1 = s1.get_value()
            self.check_type("not", s1, {Bool})
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
        r = self.class_call("(<=)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(>=)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(>)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(<)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
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
        r = self.class_call("(==)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
            self.check_types("==", s1, s2, {Int, Float, String, Bool, List, Dict, Nil, types.Class, SpaceFrame, ClassFrame, types.Enum, types.EnumValue})
            s1.update()
            s2.update()
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
        r = self.class_call("(!=)", s1, s2)
        if r is not None:
            symb_table.assign(self.dst, r.name)
        else:
            self.check_types("!=", s1, s2, {Int, Float, String, Bool, List, Dict, Nil, types.Class, SpaceFrame, ClassFrame})
            s1.update()
            s2.update()
            v1 = s1.get_value()
            v2 = s2.get_value()
            r = v1 != v2
            symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"NEQ {ir_str(self.src1)}, {ir_str(self.src2)}, {self.dst}"

class Neg(Expr):
    
    def __init__(self, src1, dst):
        self.dst = dst
        self.src1 = src1

    def exec(self):
        s1 = self.get(self.src1)
        self.check_type("-", s1, {Int, Float})
        v1 = s1.get_value()
        r = -v1
        symb_table.assign(self.dst, wrap(r))

    def __str__(self):
        return f"NEG {ir_str(self.src1)}, {self.dst}"

