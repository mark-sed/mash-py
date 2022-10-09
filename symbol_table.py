from ftplib import all_errors
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

class Fun(Symbol):
    """
    Function
    """
    ...

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

    GLOB_TBL = Frame({
        #"print?1": {ir.Print("@0")}
    })

    def __init__(self, analyzer=False):
        self.initialize()
        self.analyzer = analyzer

    def initialize(self):
        self.tbls = []
        self.tbls.append(SymbTable.GLOB_TBL)

    def push(self):
        self.tbls.append(Frame())

    def pop(self):
        return self.tbls.pop()

    def clear_all(self):
        self.initialize()

    def declare(self, symb, value):
        """
        Declares variable for the first time.
        If it already exists an error is raised.
        """
        if self.exists_top(symb):
            raise mex.Redefinition(symb)
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
            self.tbls[-1][name] = [irfun]
        else:
            # Redefinition or ambiguous redef
            for i, f in enumerate(fprev):
                # Check if argument amount ranges overlap
                if f.min_args <= max_args and f.max_args >= min_args:
                    raise mex.AmbiguousRedefinition(f"function '{name}'")
                elif f.max_args == max_args:
                    # Overridden
                    self.tbls[-1][name][i] = irfun
                    break
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
            for t in reversed(self.tbls):
                if symb in t:
                    t[symb] = value
                    return
            self.tbls[-1][symb] = value

    def get(self, symb):
        nested = False
        s = symb
        if type(symb) == list:
            s = symb[0]
            nested = True
        for t in reversed(self.tbls):
            if s in t:
                if not nested:
                    return t[s]
                else:
                    # TODO: Add when classes and spaces added
                    self.error("NOT IMPLEMENTED!!")
        raise mex.UndefinedReference(symb)

    def exists_top(self, symb):
        return symb in self.tbls[-1]

    def exists(self, symb):
        nested = False
        s = symb
        if type(symb) == list:
            s = symb[0]
            nested = True
        for t in reversed(self.tbls):
            if s in t:
                if not nested:
                    return (True, "")
                else:
                    # TODO: Add when classes and spaces added
                    self.error("NOT IMPLEMENTED!!")
        return (False, s)

    def __str__(self):
        return str([str(x) for x in self.tbls])

symb_table = SymbTable(analyzer=True)
