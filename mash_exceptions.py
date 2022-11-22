from sys import stderr

class MashException(Exception):
    pass

class UndefinedReference(MashException):
    """
    Undefined reference to a symbol
    """
    def __init__(self, msg, *args: object):
        super().__init__("Undefined reference: "+msg, *args)

class Unimplemented(MashException):
    """
    Unimplemented feature that should work
    """
    def __init__(self, msg, *args: object):
        super().__init__("Unimplemented: "+msg, *args)

class TypeError(MashException):
    """
    Type or value error
    """
    def __init__(self, msg, *args: object):
        super().__init__("Type error: "+msg, *args)

class KeyError(MashException):
    """
    Key
    """
    def __init__(self, msg, *args: object):
        super().__init__("Key error: "+msg, *args)

class IndexError(MashException):
    """
    Index/member error
    """
    def __init__(self, msg, *args: object):
        super().__init__("Index error: "+msg, *args)

class IncorrectDefinition(MashException):
    """
    Definition where it should not be or with incorrect values
    """
    def __init__(self, msg, *args: object):
        super().__init__("Incorrect definition: "+msg, *args)

class ValueError(MashException):
    """
    Value error
    """
    def __init__(self, msg, *args: object):
        super().__init__("Value error: "+msg, *args)

class Redefinition(MashException):
    """
    Symbol redefinition
    """
    def __init__(self, msg, *args: object):
        super().__init__("Redefinition: "+msg, *args)

class SyntaxError(MashException):
    """
    Syntax error
    """
    def __init__(self, msg, *args: object):
        super().__init__("Syntax error: "+msg, *args)

class AmbiguousRedefinition(MashException):
    """
    Ambiguous redefinition
    """
    def __init__(self, msg, *args: object):
        super().__init__("Ambiguous redefinition of '"+msg+"'", *args)

class ImportError(MashException):
    """
    Import error
    """
    def __init__(self, msg, *args: object):
        super().__init__("Import error: "+msg, *args)

class FlowControl(MashException):
    """
    Exceptions for controlling flow
    """

class FlowControlBreak(FlowControl):
    """
    Break
    """

class FlowControlContinue(FlowControl):
    """
    Continue
    """

class FlowControlReturn(FlowControl):
    """
    Return
    """
    def __init__(self, value, frames=1):
        self.value = value
        self.frames = frames

def warning(msg):
    print(f"Warning: {msg}", file=stderr)
