/**
Mash core library.
@author Marek Sedlacek
*/

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

}