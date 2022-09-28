from lark import Lark, Transformer

def debug(msg, opts):
    """
    Debug message
    """
    if opts.verbose:
        print("DEBUG: {}.".format(msg))


class Parser:
    """
    Parser class
    """

    def __init__(self, code, opts):
        """
        Constructor
        """
        self.code = code
        self.opts = opts
        with open("grammars/mash.lark", "r") as gfile:
            grammar = gfile.read()
        self.parser = Lark(grammar, start="start")
    
    def parse(self):
        """
        Parses mash code
        """
        parse_tree = self.parser.parse(self.code)
        if self.opts.verbose:
            print(parse_tree.pretty())
        return parse_tree


class SymbTable:
    """
    Symbolic table
    """

    def __init__(self):
        pass


class ConstTransformer(Transformer):
    """
    Tree transformer
    """
    def __init__(self, symb_table):
        """
        Transformer constructor
        """
        self.symb_table = symb_table

    def int(self, items):
        """
        Expression
        """
        return int(items[0])

    def float(self, items):
        """
        Expression
        """
        return float(items[0])

def interpret(opts, code):
    """
    Interpret mash code
    """
    debug("Parser started", opts)
    parser = Parser(code, opts)
    tree = parser.parse()
    debug("Parser finished", opts)
    if opts.parse_only:
        return
    symb_table = SymbTable()
    for i in tree.children:
        print(i.data, i.children)
    
