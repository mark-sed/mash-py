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

    def __str__(self):
        return f"{self.name} = {self.value}"

class Fun(Symbol):
    """
    Function
    """
    ...

class SymbTable(Mash):
    """
    Symbolic table
    """
    GLOB_TBL = {
        #"print?1": {ir.Print("@0")}
    }

    def __init__(self):
        self.tbls = []
        self.tbls.append(SymbTable.GLOB_TBL)

    def declare(self, symb, value):
        """
        Declares variable for the first time.
        If it already exists an error is raised.
        """
        if self.exists_top(symb):
            raise mex.Redefinition(symb)
        self.tbls[-1][symb] = value

    def assign(self, symb, value):
        """
        Assigns value to a variable.
        """
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
        return (False, f"Undefined reference to '{s}'")

    def __str__(self):
        return str(self.tbls)

symb_table = SymbTable()