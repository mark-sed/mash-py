class MashException(Exception):
    pass

class UndefinedReference(MashException):
    pass

class Unimplemented(MashException):
    pass

class TypeError(MashException):
    pass