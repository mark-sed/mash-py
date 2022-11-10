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
    new Int(self, v) internal
}

class Float {
    # new Float(self, v:Float) internal
    # new Float(self, v:Int) internal
    # new Float(self, v:String) internal
    new Float(self, v) internal
}

class String {
    new String(self, v) internal
}

class Bool {
    # new Bool(self, v:Bool) internal
    # new Bool(self, v:Int) internal
    # new Bool(self, v:Float) internal
    # new Bool(self, v:NilType) internal
    new Bool(self, v) internal
}

class List {
    new List(self) internal
    new List(self, a, *b) internal
}

class Dict {
    new Dict(self) internal
}

class NilType { 
    new NilType(self) internal
}

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

fun type(var) internal

fun id(var) internal

/** Output functions */
fun print(a) { return ""++a }
fun print(a, b, *c) { 
    r = a++" "++b
    for(i : c) {
        r = r++" "++i
    }
    return r
}
fun println() { return "\n" }
fun println(a) { return a++"\n" }
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

/**
 * Bitwise and
 * @param a First Int value
 * @param b Second Int value
 * @return Bitwise and over passed in arguments
 */
fun bitand(a, b) internal

/**
 * Bitwise or
 * @param a First Int value
 * @param b Second Int value
 * @return Bitwise or over passed in arguments
 */
fun bitor(a, b) internal

/**
 * Bitwise exclusive or
 * @param a First Int value
 * @param b Second Int value
 * @return Bitwise xor over passed in arguments
 */
fun bitxor(a, b) internal

/**
 * Bitwise inversion
 * @param a Int value
 * @return Bitwise inversion over passed in argument
 */
fun bitnot(a) internal

/**
 * Left shift
 * @param a Int value
 * @param count Amount to shift by
 * @return First argument shifted left by the amount in the second argument 
 */
fun lshift(a, count) internal

/**
 * Right shift
 * @param a Int value
 * @param count Amount to shift by
 * @return First argument shifted right by the amount in the second argument 
 */
fun rshift(a, count) internal

/** Lists functions **/
/**
 * Cartesian product of passed in lists
 * @param l1 List
 * @param l2 List
 * @return List of lists containing cartesian product of passed in arguments.
 */
fun zip(l1, l2) internal  # Change from internal to [[x, y] : x = l1, y = l2]

/**
 * Creates new list by reversing passed one
 * @param l List to reverse
 * @return new list that is reversed version of the passed one
 */
fun reverse(l) internal

/** String functions */

/**
 * Converts string to uppercase
 * @param s String to be converted
 * @return Passed in string in uppercase
 */
fun upper(s) internal

/**
 * Converts string to lowercse
 * @param s String to be converted
 * @return Passed in string in lowercase
 */
fun lower(s) internal

/**
 * Capitalized string
 * First letter is in uppercase, the rest is lowercase
 * @param s String to be capitalized
 * @return Capitalized passed in string
 */
fun capitalize(s) internal



/** Space for functions using random number generator */
space Rnd {

    /**
    * Shuffles elements in a list, not changing the passed in list
    * @param l List to be shuffled
    * @return Copy of passed in list with randomly shuffled elements
    */
    fun shuffle(l) internal

}

/** Math functions **/
space Math {

    /** Constants **/

    /** π (Ludolph's number) */
    pi = 3.141592653589793115997963468544185161590576171875

    /** e (Euler's number) */
    e = 2.718281828459045090795598298427648842334747314453125

    /** τ (2*pi)
    tau = 6.28318530717958623199592693708837032318115234375

    /** φ (Golden ratio = (1 + 5^0.5)/2) */
    phi = 1.6180339887498949025257388711906969547271728515625

    /** Euler–Mascheroni constant */
    euler_gamma = 0.57721566490153286554942724251304753124713897705078125

    /**
    * Sine
    * @param x Numeric value
    * @return Sine of x in radians
    */
    fun sin(x) internal

    /**
    * Tangent
    * @param x Numeric value
    * @return Tangent of x in radians
    */
    fun tan(x) internal

    /**
    * Cosine
    * @param x Numeric value
    * @return Cosine of x in radians
    */
    fun cos(x) internal

    /**
    * Arc sine
    * @param x Numeric value
    * @return Arc sine of x in radians
    */
    fun asin(x) internal

    /**
    * Arc tangent
    * @param x Numeric value
    * @return Arc tangent of x in radians
    */
    fun atan(x) internal
    /** Returns atan(y/x) */
    fun atan(y, x) internal

    /**
    * Arc cosine
    * @param x Numeric value
    * @return Arc cosine of x in radians
    */
    fun acos(x) internal

    /**
    * Square root function
    * Is equal to x^0.5
    * @param x Value to be calculated the square root of
    * @return Square root of passed in argument
    */
    fun sqrt(x) { return x^0.5 }

}