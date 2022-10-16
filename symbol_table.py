from ftplib import all_errors
from xml.dom.pulldom import IGNORABLE_WHITESPACE
from mash import Mash
import mash_exceptions as mex

class Symbol:

    def key(self):
        return "!!!ERROR"

class Var(Symbol):
    """
    Variable
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def key(self):
        return self.name

    def fstr(self):
        return self.value.fstr()

    def __str__(self):
        return f"{self.name} = {self.value}"

class Frame(dict):
    """
    Frame for symbol table
    """

    def __str__(self):
        return ", ".join(["{"+str(k)+": "+str(v)+"}" if type(v) != list else k+": "+str([i.str_header() for i in v]) for k, v in self.items()])

class SymbTable(Mash):
    """
    Symbolic table
    """
    RETURN_NAME = "@ret"

    def __init__(self, analyzer=False):
        self.initialize()
        self.analyzer = analyzer

    def initialize(self):
        self.tbls = []
        self.tbls.append(Frame())
        self.spaces = []

    def push(self):
        self.tbls.append(Frame())

    def pop(self, amount=1):
        for _ in range(amount):
            self.tbls.pop()

    def push_space(self, name):
        spc = Frame()
        self.declare(name, spc)
        self.spaces.append((name, spc))

    def pop_space(self):
        self.spaces.pop()

    def in_space(self):
        return len(self.spaces) > 0

    def clear_all(self):
        self.initialize()

    def declare(self, symb, value):
        """
        Declares variable for the first time.
        If it already exists an error is raised.
        """
        if self.exists_top(symb):
            raise mex.Redefinition(symb)
        if self.in_space():
            self.spaces[-1][1][symb] = value
        else:
            self.tbls[-1][symb] = value

    def define_fun(self, name, min_args, max_args, irfun):
        """
        Function re/definition
        """
        fprev = None
        try:
            fprev = self.get(name)
        except mex.UndefinedReference as e:
            pass

        if fprev is None:
            if self.in_space():
                self.spaces[-1][1][name] = [irfun]
            else:
                self.tbls[-1][name] = [irfun]
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

    def assign(self, symb, value):
        """
        Assigns value to a variable.
        """
        # In non-analyzer mode, values are to be copied
        if not self.analyzer:
            if type(value) == str:
                # TODO: Make sure that Int, Float, String, Bool are copied
                #       They should be, because Expr creates a new object
                value = self.get(value)

        if type(symb) == list:
            pass
            self.error("NOT IMPLEMENTED!!")
        else:
            #if symb[0] != "@":
            #    for t in reversed(self.tbls):
            #        if symb in t:
            #            t[symb] = value
            #            return
            if self.in_space():
                self.spaces[-1][1][symb] = value
            else:
                self.tbls[-1][symb] = value

    def get_in(self, f, symb):
        nested = False
        s = symb
        if type(symb) == list:
            s = symb[0]
            nested = True
        if s in f:
            if not nested:
                if type(f[s]) == str:
                    raise mex.UndefinedReference(str(symb))
                return f[s]
            else:
                if type(f[s]) != Frame:
                    if type(f[s]) == list or type(f[s]) == str:
                        return f[s]
                    raise mex.TypeError(f"Cannot scope type {type(f[s])}")
                return self.get_in(f[s], symb[2:])

    def get(self, symb):
        if self.in_space():
            a = self.get_in(self.spaces[-1][1], symb)
            if a is not None:
                return a
        for t in reversed(self.tbls):
            a = self.get_in(t, symb)
            if a is not None:
                return a
        if type(symb) == list:
            raise mex.UndefinedReference("".join(symb))
        raise mex.UndefinedReference(symb)

    def exists_top(self, symb):
        if type(symb) == list:
            raise mex.Unimplemented("Scoped name exitsts")
        if self.in_space():
            return symb in self.spaces[-1][1]
        else:    
            return symb in self.tbls[-1]

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
