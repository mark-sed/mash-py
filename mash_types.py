class Value():
    """
    Values
    """
    def get_value(self):
        return self.value

    def __str__(self):
        return str(self.get_value())

class String(Value):
    """
    String
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return super(str).__str__()

class Float(Value):
    """
    Float
    """
    def __init__(self, value):
        self.value = value

class Int(Value):
    """
    Float
    """
    def __init__(self, value):
        self.value = value

class Bool(Value):
    """
    Boolean
    """
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def __str__(self):
        return "true" if self.value else "false"

class Nil(Value):
    """
    Nil
    """
    def __init__(self):
        self.value = None

    def get_value(self):
        return None

    def __str__(self):
        return "nil"