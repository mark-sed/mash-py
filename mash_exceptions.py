from sys import stderr

class MashException(Exception):
    pass

class UndefinedReference(MashException):
    """
    Undefined reference to a symbol
    """
    def __init__(self, msg, *args: object):
        super().__init__("Undefined reference to '"+msg+"'", *args)

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

class Redefinition(MashException):
    """
    Symbol redefinition
    """
    def __init__(self, msg, *args: object):
        super().__init__("Redefinition of '"+msg+"'", *args)

class AmbiguousRedefinition(MashException):
    """
    Ambiguous redefinition
    """
    def __init__(self, msg, *args: object):
        super().__init__("Ambiguous redefinition of "+msg+"", *args)

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

def warning(msg):
    print(f"Warning: {msg}", file=stderr)
