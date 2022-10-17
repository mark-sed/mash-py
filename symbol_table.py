from mash import Mash
import mash_exceptions as mex

class Frame(dict):
    """
    Frame for symbol table
    """

    def __str__(self):
        return ", ".join(["{"+str(k)+": "+str(v)+"}" if type(v) != list else k+": "+str([i.str_header() for i in v]) for k, v in self.items()])

class SpaceFrame(Frame):
    """
    Name space
    """

    def __init__(self, name):
        self.name = name

class ClassFrame(Frame):
    """
    Class
    """

    def __init__(self, name):
        self.name = name

class SymbTable(Mash):
    """
    Symbolic table
    """
    RETURN_NAME = "@ret"

    def __init__(self, analyzer=False):
        self.initialize()
        self.analyzer = analyzer

    def initialize(self):
        self.frames = [Frame()]
        self.prefix = []
        self.index = 0
        self.fun_depth = 0

    def inc_depth(self):
        self.fun_depth += 1

    def dec_depth(self):
        self.fun_depth -= 1

    def push(self):
        self.index += 1
        self.frames.insert(self.index, Frame())

    def pop(self, amount=1):
        for _ in range(amount):
            self.frames.pop()
            self.index -= 1

    def top(self):
        return self.frames[self.index]

    def scope(self):
        if self.fun_depth > 0:
            return reversed(self.frames[1:])
        return reversed(self.frames)

    def in_struct(self):
        ...

    def push_space(self, name):
        ...
        
    def pop_space(self):
        ...

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

    def define_fun(self, name, min_args, max_args, irfun):
        """
        Function re/definition
        """
        ...

    def assign(self, symb, value):
        """
        Assigns value to a variable.
        """
        if type(symb) == list:
            # Also handle global
            raise mex.Unimplemented("Assignment to scope var")
        else:
            for f in self.scope():
                if symb in f:
                    f[symb] = value
                    return
            self.top()[symb] = value

    def get(self, symb):
        if type(symb) == list:
            raise mex.Unimplemented("Scope var get")
        else:
            for f in self.scope():
                if symb in f:
                    return f[symb]
            raise mex.UndefinedReference(symb)

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
        ts = []
        for c, x in enumerate(self.tbls):
            ts.append(str(c)+": ["+str(x)+"]")
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