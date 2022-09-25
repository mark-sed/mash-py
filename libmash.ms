/**
Mash core library.
@author Marek Sedlacek
*/

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
fun abs(x) = x > 0 ? x : -x

/**
 * Integer to character conversion
 * @param c Character's UNICODE value to convert to string
 * @return Passed in argument converted to UNICODE character as a string
 */
fun chr(c) = # [! internal !]

