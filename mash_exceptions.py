from sys import stderr

class MashException(Exception):
    pass

class UndefinedReference(MashException):
    pass

class Unimplemented(MashException):
    pass

class TypeError(MashException):
    pass

def warning(msg):
    print(f"Warning: {msg}", file=stderr)
