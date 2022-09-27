/**
Mash core library.
@author Marek Sedlacek
*/

/**
 * Integer value
 */
class Int {

    /**
     * Constructor to cast parameter to Int
     */
    Int(x) {
        # [!internal!]
    }
}

/**
 * Floating point value
 */
class Float {

    /**
     * Constructor to cast parameter to Float
     */
    Float(x) {
        # [!internal!]
    }
}

/**
 * List type class
 */
class List {

    /**
     * Constructor to cast parameter to a list
     * @param x Value to be converted to a list
     */
    List(x) { 
        # [!internal!]
    }

    /**
     * Constructor to create an empty list.
     * This is the same as writing `[]`
     */
    List() {
        # [!internal!]
    }

    # TODO: Other methods
}

class Dict {

    /**
     * Constructor to create an empty dictionary.
     * This is the same as writing `{,}`
     */
    Dict() {
        # [!internal!]
    }

    # TODO: Other methods
}

/**
 * File class
 */ 
class File {

    /**
     * Opens file
     * @param path Path to the file
     * @param mode File access mode
     *             "r" for reading
     *             "w" for writing
     *             "a" for appending
     */
    File(path, mode="r") { 
        # [!internal!] 
    }

    /**
     * Writes first argument to the file
     * @param msg Value to be printed to the file
     */
    fun print(msg) { 
        # [!internal!] 
    }

    /**
     * Writes first argument to the file and appends a new line symbol
     * @param msg Value to be printed to the file
     */
    fun println(msg) {
        print(msg+"\n")
    }

    /**
     * Reads contents of the file into a String
     * @return Contents of the file as a String
     */
    fun read() { 
        # [!internal!] 
    }

    /**
     * Reads one line of the file
     * @return One line from the file
     */
    fun readln() { 
        # [!internal!] 
    }

    /**
     * Reads all lines of the file
     * @return List with each line without \n of the file as its elements
     */
    fun read_lines() { 
        # [!internal!] 
    }

    /**
     * Parses opened file as a CSV file
     * @param delim Delimiter used in the CSV file
     * @return File parsed into list of list
     */
    fun read_csv(delim=",") { 
        # [!internal!] 
    }
}

/**
 * Namespace for working with random values and RNG
 */
space Rand {

    /**
     * Sets explicit seed value for the RNG
     * @param seed Seed for the RNG
     */
    fun seed(seed) { 
        # [!internal!] 
    }

    /**
     * Random integer generator
     * @param min Minimum possible value to be generated (including this value)
     * @param max Maximum possible value to be generated (including this value)
     * @return Random integer from specified range
     */
    fun int(min, max) { 
        # [!internal!] 
    }

    /**
     * Random float generator
     * @param min Minimum possible value to be generated (including this value)
     * @param max Maximum possible value to be generated (including this value)
     * @return Random float from specified range
     */
    fun float(min=0.0, max=1.0) { 
        # [!internal!] 
    }
}

# Built-in functions

/**
 * Absolute value
 * @param x Numberic value
 * @return Absolute value of passed in argument
 */
fun abs(x) = x > 0.0 ? x : -x

/**
 * Integer to character conversion
 * @param c Character's UNICODE value to convert to string
 * @return Passed in argument converted to UNICODE character as a string
 */
fun chr(c) = # [! internal !]

/**
 * Fliters second argument by calling all its elements as parameters to the function that is the first argument.
 * If the function returns True, this element is added to the list that will be returned.
 * @param f Filter function, that returns bool and takes one argument
 * @param l List of elements to be filtered
 * @return Second argument filtered by function in the first argument
 */ 
fun filter(f, l) = [x if f(x) : x = l]

/**
 * Map function.
 * Applied passed in function to all elements in the second argument
 * @param f Function to be applied to elements in the second argument
 * @param l List of values to be mapped
 * @return List of elements in the second argument after being passed into the first argument
 */
fun map(f, l) = [f(x) : x = l]

/**
 * Maximum function
 * @param a1 First value
 * @param a2 Second value
 * @return a1 if a1 is bigger than a2, otherwise a2
 */
fun max(a1, a2) = a1 > a2 ? a1 : a2
fun max(l) {
    biggest = l[0]
    for(a: l[1:]) {
        if(a > biggest) {
            biggest = a
        }
    }
    return biggest
}

/**
 * Minimum function
 * @param a1 First value
 * @param a2 Second value
 * @return a1 if a1 is smaller than a2, otherwise a2
 */
fun min(a1, a2) = a1 < a2 ? a1 : a2
fun min(l) {
    smallest = l[0]
    for(a: l[1:]) {
        if(a < smallest) {
            smallest = a
        }
    }
    return smallest
}

/**
 * Converts character to its ordinal value
 * @param c String of length 1
 * @return Ordinal value of character in passed in string
 */
fun ord(c) = # [!internal!]

/**
 * Sum of elements in passed in list and start value
 * @param l List to be summed up
 * @param start Starting value of the sum
 * @return Sum of all elements in l and start
 */
fun sum(l, start=0) {
    for(i: l) {
        start += i
    }
    return start
}

/**
 * Returns a proxy object that delegates method calls to parent of
 * passed in argument. This is useful for invoking overriden methods.
 * @param obj Object to get the parent of
 * @return Parent proxy object of passed in object
 */
fun super(obj) = # [!internal!]

/**
 * Returns type of passed in object.
 * @param obj Object to get the type of
 * @return Returns type of passed in object
 */
fun type(obj) = # [!internal!]

/**
 * Does cartesian product of passed in lists
 * @param l1 List
 * @param l2 List
 * @return List of lists containing cartesian product of passed in arguments.
 */
fun zip(l1, l2) = [[x, y] : x = l1, y = l2]
# fun zip(..)

## Math

/**
 * Sinus
 * @param x Numeric value
 * @return Sinus of x
 */
fun sin(x) = # [!internal!]

/**
 * Tangent
 * @param x Numeric value
 * @return Tangent of x
 */
fun tan(x) = # [!internal!]

/**
 * Cosine
 * @param x Numeric value
 * @return Cosine of x
 */
fun cos(x) = # [!internal!]

# TODO: More math funcs
# TODO: Methods for operators (add, mul...)