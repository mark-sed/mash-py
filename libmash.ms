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

fun shuffle(l) internal
