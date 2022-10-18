from mash import Mash
import mash_exceptions as mex

class Frame(dict):
    """
    Frame for symbol table
    """

    def __init__(self, shadowing=False, *args, **kwargs):
        self.shadowing = shadowing
        super(Frame, self).__init__(*args, **kwargs)

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

    def __init__(self, name):
        self.name = name
        super(SpaceFrame, self).__init__(True)

class ClassFrame(Frame):
    """
    Class
    """

    def __init__(self, name):
        self.name = name
        super(ClassFrame, self).__init__(True)


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
        self.fun_depth = 0
        self.spaces = []

    def push(self, shadowing=False):
        self.index += 1
        self.frames.insert(self.index, Frame(shadowing))

    def pop(self, amount=1):
        for _ in range(amount):
            self.frames.pop()
            self.index -= 1

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
        self.index += 1
        #print(f"\nAfter pushing space {name}:", self)
        
    def pop_space(self):
        self.spaces.pop()
        self.frames.pop()
        self.index -= 1

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
        try:
            fprev = self.get(name)
        except mex.UndefinedReference:
            pass

        if fprev is None:
            self.assign(name, [irfun])
        else:
            # Redefinition or ambiguous redef
            for i, f in enumerate(fprev):
                # Check if argument amount ranges overlap
                if f.min_args <= max_args and f.max_args >= min_args and f.max_args != max_args:
                    raise mex.AmbiguousRedefinition(f"function '{name}'")
                elif f.max_args == max_args:
                    # Overridden
                    if self.in_space():
                        self.spaces[-1][1][name][i] = irfun
                    else:
                        self.tbls[-1][name][i] = irfun
                    break
            else:
                if self.in_space():
                    self.spaces[-1][1][name].append(irfun)
                else:
                    self.tbls[-1][name].append(irfun)

    def get_frame(self, symb):
        if type(symb) == list:
            ...
        else:
            scope = self.frames[:]
            if self.fun_depth > 0:
                scope = self.frames[1:]
            for f in reversed(scope):
                if symb in f:
                    return f
                if f.shadowing:
                    break
        return None

    def assign(self, symb, value):
        """
        Assigns value to a variable.
        """
        f = self.get_frame(symb)
        if f is None:
            self.top()[symb] = value
        else:
            f[symb] = value
        #print(f"\nAfter assignment of {symb} = {value}:", self)

    def get(self, symb):
        f = self.get_frame(symb)
        if f is None:
            if type(symb) == list:
                raise mex.UndefinedReference("".join(symb))
            raise mex.UndefinedReference(symb)
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
            return False, str(symb)
        return True, ""

    def __str__(self):
        ts = ["Symbolic table:"]
        for c, x in enumerate(self.frames):
            ts.append(str(c)+": {\n"+x.fstr(0)+"\n}")
        ts.append("Spaces: "+str([x.name for x in self.spaces]))
        return "\n".join(ts)

symb_table = SymbTable(analyzer=True)

"""
fun f() {
    space A {
        a
    }
    space B {
        space C {
            
        }
    }
    A::a = 4
    f() <-
}

[
    f() : Fun
] <-
[
    A : [
        a : Nil()
    ]
    B : [
        C : [

        ]
    ]
]
[
    A : [
        a : 4
    ]
    B : [
        C : [
            
        ]
    ]
]

"""

"""
fun a() {
    fun b() {
        "1"
    }
    fun c() {
        a = "2"
        b()
    }
    c()
}
a()

[
    a : Fun
]
[
    b : Fun
    c : Fun
]
[
    a : Int(2)

]

In a function call, the frame pointer has to be moved the the frame in which function appears.
After return the previous frame index has to be restored (stack of indexes)

b = "hi"
if(x) {
    fun b() {
        a = 4
    }
    if(y) {
        a = 6
        b() <-
        a # HAS TO BE 6, NOT 4!
    }
}

[
    b : String(hi)
]
[
    b : Fun
]
[
    a : Int
]

If construct frame is pushed, then it should be always added to a list, but if function is called, then 
"""

"""
a = 5

fun foo() {
    a = 0  # new var
    ::a = 4  # Global var

    space A {
        a = 2  # new var

        if(a == 2) { # A::a
            a = 4  # A::a
            @a = 8 # a in fun foo
            b # new var
        }

        b # Nil, b is not in scope
        a # Prints 4
    }

    return a # return 8
}

function, classes and spaces overshadow existing nonlocal and global variables
other structures (if, while, unnamed block) dont overshadow, but reassign
"""