/**
Mash core library.
@author Marek Sedlacek
*/

/** Class/Object methods */
class Type {
    
}

class Int {
    # new Int(self, v:Int) internal
    # new Int(self, v:Float) internal
    # new Int(self, v:Bool) internal
    # new Int(self, v:String) internal
    new Int(self, v=0) internal
}

class Float {
    # new Float(self, v:Float) internal
    # new Float(self, v:Int) internal
    # new Float(self, v:String) internal
    new Float(self, v=0.0) internal
}

class String {
    new String(self, v="") internal

    fun len(self) internal
    #fun upper(self) internal
}

class Bool {
    # new Bool(self, v:Bool) internal
    # new Bool(self, v:Int) internal
    # new Bool(self, v:Float) internal
    # new Bool(self, v:NilType) internal
    new Bool(self, v=false) internal
}

class List {
    new List(self) internal
    new List(self, a, *b) internal

    fun len(self) internal
}

class Dict {
    new Dict(self) internal
}

class NilType { 
    new NilType(self) internal
}

fun get_args() internal
args = get_args()

class StopIteration {}

class Range {
    new Range(self, start, end, step=1) {
        self.start = start
        self.end = end
        self.step = step
        self.i = start
    }

    fun __next(self) {
        if(self.step >= 0 and self.i >= self.end) return StopIteration
        if(self.step < 0 and self.i <= self.end) return StopIteration
        r = self.i
        self.i += self.step
        return r
    }
}

class Super {
    new Super(self, type:Type, obj) {
        self.type = type
        self.obj = obj
    }
}

fun type(var) internal

fun id(var) internal

fun doc(obj) internal

class File {

    enum FileMode {
        READ,       # "r"
        WRITE,      # "w"
        CREATE,     # "x"
        APPEND,     # "a"
        READ_WRITE  # "+"
    }

    fun mode2str(self, mode:FileMode) {
        if(mode == ::File::FileMode::READ) return "r"
        if(mode == ::File::FileMode::WRITE) return "w"
        if(mode == ::File::FileMode::CREATE) return "x"
        if(mode == ::File::FileMode::APPEND) return "a"
        if(mode == ::File::FileMode::READ_WRITE) return "+"
    }

    fun str2mode(self, mode:String) {
        if(mode == "r") return ::File::FileMode::READ
        if(mode == "w") return ::File::FileMode::WRITE
        if(mode == "x") return ::File::FileMode::CREATE
        if(mode == "a") return ::File::FileMode::APPEND
        if(mode == "+") return ::File::FileMode::READ_WRITE
    }

    new File(self, path:String, mode:String="r") {
        self.path = path
        self.mode = mode
    }

    new File(self, path:String, mode:FileMode) {
        self.path = path
        self.mode = self.mode2str(mode)
    }

    fun write(self, content:String) internal

    fun read(self, size:Int=-1) internal

    fun readln(self) internal

    fun readlines(self) internal

    fun open(self) internal

    fun close(self) internal
}

fun readln(prompt="") internal

fun exit(code=0) internal

/** Output functions */
fun print(a) { return ""++a; }
fun print(a, b, *c) { 
    r = a++" "++b
    for(i : c) {
        r = r++" "++i
    }
    return r
}
fun println() { return "\n"; }
fun println(a) { return a++"\n"; }
fun println(a, b, *c) { 
    r = a++" "++b
    for(i : c) {
        r = r++" "++i
    }
    return r++"\n"
}

fun vardump(*var) internal

/** Attributes */
fun getattr(object, name) internal
fun getattr(object, name, default) internal
fun setattr(object, name, value) internal

/** Bit-wise operators **/

fun bitand(a, b) internal
d"""
Bitwise and
@param a First Int value
@param b Second Int value
@return Bitwise and over passed in arguments
"""

fun bitor(a, b) internal
d"""
Bitwise or
@param a First Int value
@param b Second Int value
@return Bitwise or over passed in arguments
"""

fun bitxor(a, b) internal
d"""
Bitwise exclusive or
@param a First Int value
@param b Second Int value
@return Bitwise xor over passed in arguments
"""

fun bitnot(a) internal
d"""
Bitwise inversion
@param a Int value
@return Bitwise inversion over passed in argument
"""

fun lshift(a, count) internal
d"""
Left shift
@param a Int value
@param count Amount to shift by
@return First argument shifted left by the amount in the second argument
"""

fun rshift(a, count) internal
d"""
Right shift
@param a Int value
@param count Amount to shift by
@return First argument shifted right by the amount in the second argument
"""

/** Lists functions **/
fun zip(l1, l2) internal  # Change from internal to [[x, y] : x = l1, y = l2]
d"""
Cartesian product of passed in lists
@param l1 List
@param l2 List
@return List of lists containing cartesian product of passed in arguments.
"""

fun reverse(l) internal
d"""
Creates new list by reversing passed one
@param l List to reverse
@return new list that is reversed version of the passed one
"""

/** String functions */

fun upper(s) internal
d"""
Converts string to uppercase
@param s String to be converted
@return Passed in string in uppercase
"""

fun lower(s) internal
d"""
Converts string to lowercse
@param s String to be converted
@return Passed in string in lowercase
"""

fun capitalize(s) internal
d"""
Capitalized string
First letter is in uppercase, the rest is lowercase
@param s String to be capitalized
@return Capitalized passed in string
"""

space Rnd {
    d"""Space for functions using random number generator"""

    fun shuffle(l) internal
    d"""
    Shuffles elements in a list, not changing the passed in list
    @param l List to be shuffled
    @return Copy of passed in list with randomly shuffled elements
    """
}

space Math {
    d"""
    Math functions
    """

    /** ?? (Ludolph's number) */
    pi = 3.141592653589793115997963468544185161590576171875

    /** e (Euler's number) */
    e = 2.718281828459045090795598298427648842334747314453125

    /** ?? (2*pi)
    tau = 6.28318530717958623199592693708837032318115234375

    /** ?? (Golden ratio = (1 + 5^0.5)/2) */
    phi = 1.6180339887498949025257388711906969547271728515625

    /** Euler???Mascheroni constant */
    euler_gamma = 0.57721566490153286554942724251304753124713897705078125

    fun sin(x) internal
    d"""
    Sine
    @param x Numeric value
    @return Sine of x in radians
    """

    fun tan(x) internal
    d"""
    Tangent
    @param x Numeric value
    @return Tangent of x in radians
    """

    fun cos(x) internal
    d"""
    Cosine
    @param x Numeric value
    @return Cosine of x in radians
    """

    fun asin(x) internal
    d"""
    Arc sine
    @param x Numeric value
    @return Arc sine of x in radians
    """

    fun atan(x) internal
    d"""
    Arc tangent
    @param x Numeric value
    @return Arc tangent of x in radians
    """
    fun atan(y, x) internal
    d"""
    Returns atan(y/x)
    """

    fun acos(x) internal
    d"""
    Arc cosine
    @param x Numeric value
    @return Arc cosine of x in radians
    """

    fun sqrt(x) {
        d"""
        Square root function
        * Is equal to x^0.5
        * @param x Value to be calculated the square root of
        * @return Square root of passed in argument
        """
        return x^0.5;
    }

}

