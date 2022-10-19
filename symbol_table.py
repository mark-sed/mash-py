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
    Class frame
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
            self.assign(name, [irfun])
        else:
            # Redefinition or ambiguous redef
            for i, f in enumerate(fprev):
                # Check if argument amount ranges overlap
                if f.min_args <= max_args and f.max_args >= min_args and f.max_args != max_args:
                    raise mex.AmbiguousRedefinition(f"function '{name}'")
                elif f.max_args == max_args:
                    # Overridden
                    fprev[i] = irfun
                    break
            else:
                fprev.append(irfun)

    def search_scope(self, symb, scope, write, ret_top=False):
        s = symb[0]
        for f in reversed(scope):
            if s in f:
                if len(symb) == 1:
                    return f
                else:
                    return self.search_scope(symb[2:], [f[s]], write, ret_top)
            if write and f.shadowing:
                break
        if ret_top and len(symb) == 1:
            return scope[-1]
        return None

    def get_frame(self, symb, write=False, ret_top=False):
        if type(symb) != list:
            symb = [symb]

        if symb[0] == "@":
            # Non-local var
            write = False
            symb = symb[1::]
        elif symb[0] == "::":
            # Global var
            scope = self.frames[0:1]
            return self.search_scope(symb[1:], scope, write, ret_top=ret_top)

        if self.shadow_depth > 0 and write:
            scope = self.frames[1:self.index+1]
        else:
            scope = self.frames[:self.index+1]
        return self.search_scope(symb, scope, write, ret_top=ret_top)

    def assign(self, symb, value):
        """
        Assigns value to a variable.
        """
        if not self.analyzer:
            if type(value) == str:
                # TODO: Make sure that Int, Float, String, Bool are copied
                #       They should be, because Expr creates a new object
                value = self.get(value)
        f = self.get_frame(symb, True, True)
        if f is None:
            raise mex.UndefinedReference("".join(symb))

        if type(symb) == list:
            f[symb[-1]] = value
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
            return False, "".join(symb)
        return True, ""

    def __str__(self):
        ts = ["Symbolic table:"]
        for c, x in enumerate(self.frames):
            ts.append(("--> " if self.index == c else "") + str(c)+": {\n"+x.fstr(0)+"\n}")
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