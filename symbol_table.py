from mash import Mash
import mash_exceptions as mex

class Frame(dict):
    """
    Frame for symbol table
    """

    def __init__(self, shadowing=False, *args, **kwargs):
        self.shadowing = shadowing
        super(Frame, self).__init__(*args, **kwargs)

    def get_value(self):
        return self

    def fstr(self, indent=0):
        spc = indent*"    "
        endspc = (indent-1)*"    " if indent > 0 else ""
        if type(self) == SpaceFrame:
            s = [f"SpaceFrame {self.name}["]
        elif type(self) == ClassFrame:
            s = [f"ClassFrame {self.name}["]
        else:
            s = ["Frame["]
        for k, v in self.items():
            if type(v) == list:
                s.append("\n"+spc+str(k)+": "+str([i.str_header() for i in v]))
            elif type(v) == Frame or type(v) == SpaceFrame or type(v) == ClassFrame:
                s.append("\n"+spc+str(k)+": "+v.fstr(indent=indent+1))
            elif type(v) == str:
                s.append("\n"+spc+str(k)+": "+str(v))
            else:
                s.append("\n"+spc+str(k)+": "+v.type_name()+"("+str(v)+")")
        s.append("\n"+endspc+"]")
        return "".join(s)

class SpaceFrame(Frame):
    """
    Name space
    """

    def __init__(self, name, frame=None):
        self.name = name
        if frame is None:
            super(SpaceFrame, self).__init__(True)
        else:
            super(SpaceFrame, self).__init__(True, frame)

    def __eq__(self, other):
        return id(self) == id(other)

    def type_name(self):
        return self.name

    def __str__(self):
        return f"<space {self.name}>"

class ClassFrame(Frame):
    """
    Class frame
    """

    def __init__(self, name, extends):
        self.name = name
        self.extends = extends
        super(ClassFrame, self).__init__(True)

    def __eq__(self, other):
        return id(self) == id(other)

    def type_name(self):
        return self.name

    def instance(self):
        from mash_types import Class
        return Class(self.name, self)

    def __str__(self):
        return f"<class {self.name}>"

class SymbTable(Mash):
    """
    Symbolic table
    """
    RETURN_NAME = "$ret"

    def __init__(self, analyzer=False):
        self.initialize()
        self.analyzer = analyzer

    def initialize(self):
        self.frames = [Frame()]
        self.index = 0
        self.shadow_depth = 0
        self.spaces = []

    def push(self, shadowing=False):
        self.index += 1
        if shadowing:
            self.shadow_depth += 1
        self.frames.insert(self.index, Frame(shadowing))

    def pop(self, amount=1):
        for _ in range(amount):
            if self.frames[self.index].shadowing:
                self.shadow_depth -= 1
            del self.frames[self.index]
            self.index -= 1

    def move_top(self, f):
        # No need to move shadow_depth, since this is only in case of function call, which is shadowing
        # And the frame will be restored after return
        self.index = self.frames.index(f)

    def top(self):
        return self.frames[self.index]

    def in_space(self):
        return len(self.spaces) > 0

    def push_space(self, name):
        f = SpaceFrame(name)
        if self.in_space():
            self.top()[name] = f
            self.spaces.append(f)
        else:
            self.top()[name] = f
            self.spaces.append(f)
        self.frames.append(f)
        self.shadow_depth += 1
        self.index += 1
        #print(f"\nAfter pushing space {name}:", self)
        
    def pop_space(self):
        self.spaces.pop()
        self.pop()

    def push_class(self, name, extends):
        f = ClassFrame(name, extends)
        if self.in_space():
            self.top()[name] = f
            self.spaces.append(f)
        else:
            self.top()[name] = f
            self.spaces.append(f)
        self.frames.append(f)
        self.shadow_depth += 1
        self.index += 1
        
    def pop_class(self):
        self.spaces.pop()
        self.pop()

    def clear_all(self):
        self.initialize()

    def declare(self, symb, value):
        """
        Declares variable for the first time.
        If it already exists an error is raised.
        """
        if self.exists_top(symb):
            raise mex.Redefinition(symb)
        self.top()[symb] = value
        #print(f"\nAfter declaration of {symb}:", self)

    def define_fun(self, name, min_args, max_args, irfun):
        """
        Function re/definition
        """
        fprev = None
        fprevfr = self.get_frame(name, True)
        if fprevfr is not None:
            fprev = fprevfr[name]

        if fprev is None or type(fprev) != list:
            self.assign(name, [irfun], fun_arg=True)
        else:
            # Redefinition or ambiguous redef
            for i, f in enumerate(fprev):
                # Check if argument amount ranges overlap
                if f.min_args <= max_args and f.max_args >= min_args and f.max_args != max_args:
                    raise mex.AmbiguousRedefinition(f"function '{name}'")
                elif f.max_args == max_args:
                    types1 = [k[1] if type(k) == tuple else None for k, _ in f.args]
                    types2 = [k[1] if type(k) == tuple else None for k, _ in irfun.args]
                    if types1 != types2:
                        continue
                    # Overridden
                    fprev[i] = irfun
                    break
            else:
                # Insert so that the list is ascending based on amount of arguments
                for i, f in enumerate(fprev):
                    if max_args <= f.max_args:
                        fprev.insert(i, irfun)
                        break
                else:
                    fprev.append(irfun)

    def search_scope(self, symb, scope, write, ret_top=False):
        from mash_types import Class
        obj_find = False
        move_am = 1
        if symb[0] == ".":
            s = symb[1]
            move_am = 2
            obj_find = True
            if self.analyzer:
                return False
        elif symb[0] == "::":
            s = symb[1]
            move_am = 2
        else:
            s = symb[0]

        for f in reversed(scope):
            if not issubclass(type(f), Frame) and type(f) != Class:
                return (f, symb)
            if s in f:
                if len(symb) <= 2:
                    if obj_find:
                        return f.attr
                    return f
                else:
                    if obj_find:
                        return self.search_scope(symb[move_am:], [f[s].attr], write, ret_top)
                    return self.search_scope(symb[move_am:], [f[s]], write, ret_top)
            if write and (obj_find or f.shadowing):
                break
        if ret_top and len(symb) <= 2:
            return scope[-1]
        return None

    def search_scope_list(self, symb, scope, write):
        from mash_types import Class
        obj_find = False
        move_am = 1
        if symb[0] == ".":
            s = symb[1]
            move_am = 2
            obj_find = True
            if self.analyzer:
                return False
        elif symb[0] == "::":
            s = symb[1]
            move_am = 2
        else:
            s = symb[0]
        
        for f in reversed(scope):
            if not issubclass(type(f), Frame) and type(f) != Class:
                return [(f, symb)]
            if s in f:
                if len(symb) <= 2:
                    if obj_find:
                        return [f.attr]
                    return [f]
                else:
                    if obj_find:
                        return [f.attr]+self.search_scope_list(symb[move_am:], [f[s]], write)
                    return [f]+self.search_scope_list(symb[move_am:], [f[s]], write)
            if write and (obj_find or f.shadowing):
                break
        if type(scope[-1]) != list:
            return [scope[-1]]
        return scope[-1]

    def get_frame(self, symb, write=False, ret_top=False, flist=False):
        if type(symb) != list:
            symb = [symb]

        if symb[0] == "@":
            # Non-local var
            write = False
            symb = symb[1::]
        elif symb[0] == "::":
            # Global var
            scope = self.frames[0:1]
            if flist:
                return self.search_scope_list(symb[1:], scope, write)
            return self.search_scope(symb[1:], scope, write, ret_top=ret_top)

        if self.shadow_depth > 0 and write:
            scope = self.frames[1:self.index+1]
        else:
            scope = self.frames[:self.index+1]
        if flist:
            return self.search_scope_list(symb, scope, write)
        return self.search_scope(symb, scope, write, ret_top=ret_top)

    def assign(self, symb, value, fun_arg=False):
        """
        Assigns value to a variable.
        """
        if not self.analyzer and not fun_arg:
            if type(value) == str or (type(value) == list and len(value) > 0 and type(value[0]) == str):
                # TODO: Make sure that Int, Float, String, Bool are copied
                #       They should be, because Expr creates a new object
                value = self.get(value)
        obj_access = False
        if not self.analyzer and type(symb) == list and len(symb) > 2 and symb[-2] == ".":
            obj_access = True
            f = self.get_frame(symb, True, True, flist=True)
        else:
            f = self.get_frame(symb, True, True)
        
        if type(f) == tuple:
            f = f[0].access(f[1][1:])
        elif type(f) == list and len(f) > 0 and type(f[-1]) == tuple:
            f = f[-1][0].access(f[1][1:])
        if f is None:
            raise mex.UndefinedReference("".join(symb))
        elif type(f) == bool:
            return

        if obj_access:
            f[-1][symb[-1]] = value
        elif type(symb) == list:
            f[symb[-1]] = value
        else:
            f[symb] = value
        #print(f"\nAfter assignment of {symb} = {value}:", self)

    def get(self, symb):
        f = self.get_frame(symb)
        
        if type(f) == tuple:
            f = f[0].access(f[1][1:])
        elif type(f) == list and len(f) > 0 and type(f[-1]) == tuple:
            f = f[-1][0].access(f[1][1:])
        if f is None:
            if type(symb) == list:
                raise mex.UndefinedReference("".join(symb))
            raise mex.UndefinedReference(symb)
        elif type(f) == bool:
            return
        
        if type(symb) == list:
            return f[symb[-1]]
        return f[symb]

    def exists_top(self, symb):
        if type(symb) == list:
            raise mex.Unimplemented("Scope exists")
        return symb in self.top()

    def exists(self, symb):
        try:
            self.get(symb)
        except mex.UndefinedReference:
            return False, "".join(symb)
        return True, ""

    def __str__(self):
        ts = ["Symbolic table:"]
        for c, x in enumerate(self.frames):
            ts.append(("--> " if self.index == c else "") + str(c)+": {\n"+x.fstr(0)+"\n}")
        ts.append("Spaces: "+str([x.name for x in self.spaces]))
        return "\n".join(ts)

symb_table = SymbTable(analyzer=True)
