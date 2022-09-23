/*
Showcase of basic mash syntax
Comments within slash star are multiline comments
*/
# Comments can also be one line when # is used or //

# Modules can be at any point imported and are valid within the imported scope
import gui

# Objects and functions can be accessed from the module using its name
window = gui.Window("Test")

# Variables are dynamically typed 
window = nil  # nil is special value and it's the only value for type "nil"

# There are other types, which are all classes
fourtytwo = Int("42")  # The value will be parsed from string
flaotytwo = Float("42.0");  # Semicolons can be used
string42 = String(42)
is42 = Bool("true")
is43 = Bool("False") # Everything that is not "true" (in any capitalization) will be false

# Every class, including the built-in types, extends class Object and has built-in conversion to String
# and unique ID
out.println(Bool("TRUE"))  # Prints "true\n"

# The extention of the Object class is implicit
class MyClass {
    value1
    value2
    value3

    MyClass(arg1) {
        # Constructor
        value1 = arg1
        # Object value can be refered to also using `this` keyword
        this.value2 = arg1 * 2
        # Unitialized object variables will be set to `nil`
    }

    fun _to_string() {
        # Overriding implicit String conversion method
        # Here String interpolation is used to embed argument values into the string
        return f"value1 = {value1}; value2 = {value2}; value3 = {value3}"
    }

    # Lambda getter
    fun getMul1(c) = value1 * c
}

# New class instance can be created by calling class constructor
myObject = MyClass(42)
out.println(myObject)  # This will print string returned by to_string implemented above

# During a runtime built-in function `_type()` can be accessed to determine objects type and ID can be also accessed
otherObj = MyClass(43)
if(myObject._type() == otherObj._type() && myObject._id() != otherObj._id()) {
    out.println("The objects have same type, but different ID.")
}

# When checking for class type with object, following can be done
# Class name without constructor call is an instance of _Type object
otherObj = 0
if(otherObj._type() == Int) {
    println("otherObj is an integer")
}

# _type() method returns a _Type class object and so it can be printed using the implicit _to_string method
out.println(myObject._type())  # Prints "MyObject\n"

# A lambda function can also be anonymous
lambdas = [fun (a, b) = a * b, fun (a, b) = a / b]
lambdas[1](84, 2)
