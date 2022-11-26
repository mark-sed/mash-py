/**
 * Calculates resulting value of collatz conjecture for a given value
 * and prints the intermediate value of it.
 */

fun collatz(n) {
    steps = 0
    while(n != 1) {
        if(n % 2 == 0) {
            n //= 2
        }
        else {
            n = 3*n + 1
        }
        n++" "
        steps += 1
    }
}

while(true) {
    v = readln("Value to test collatz conjecture for: ")
    v = Int(v)
    ~collatz(v)
    "\n\n"
}
