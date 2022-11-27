
# Collatz Conjecture

The Collatz conjecture, also known as the _3n + 1 problem_ is unsolved problem, which states, that:

If a given function, described bellow, is applied to every positive integer, the value will eventually
result to 1.

If the given value is even, then it is to be devided by 2. Otherwise it is to be multiplied by 3 and 1 added.

In modular arithmetic notation, this function _f_ can be defined as:

```


#| equation
fun f(n) {
    if(n % 2 == 0) return n//2
    else return 3*n + 1
}


```

In Mash, a method to calculate resulting value for a given integer, can be written as bellow.

Intermediete values and total amount of steps is being counted to better showcase how this function works.

```


fun collatz(n) {
    d"""
    Collatz conjecture test
    @param n Value to test the collatz conjecture for
    @return nil
    @note Prints intermediate values to the stdout
    """
    while(n != 1) {
        if(n % 2 == 0) {
            n //= 2
        }
        else {
            n = 3*n + 1
        }
        n++" "
    }
}


```

Invoking this function for a random value, gives the following output

```

~collatz(42)
"\n\n"


```
_[Output]:_
```
21 64 32 16 8 4 2 1 


```

We can now look at how the number of steps differs for different values using the following function:

```

fun collatz_steps(n) {
    d"""
    Collatz conjecture test that returns the number of steps needed
    @param n Value to test the collatz conjecture for
    @return Number of steps needed for the value to get to 1
    """
    steps = 0
    while(n != 1) {
        if(n % 2 == 0) {
            n //= 2
        }
        else {
            n = 3*n + 1
        }
        steps += 1
    }
    return steps
}


```

Lets first calculate the number of steps for _n < 16_: 

```

tbl = [0]
for(i : [1..16]) {
    tbl += [collatz_steps(i)]
}

"Number of steps for n <= 15:\n"
#| table
tbl
"\n\n"


```
_[Output]:_
```
Number of steps for n <= 15:
[0, 0, 1, 7, 2, 5, 8, 16, 3, 19, 6, 14, 9, 9, 17, 17]


```

Lets now plot the number of steps for even more values to a graph:
```

tbl = [0]
for(i : [1..501]) {
    tbl += [collatz_steps(i)]
}

"Number of steps for n <= 500:\n"
tbl
#~Grph::plot(tbl)

```
_[Output]:_
```
Number of steps for n <= 500:
[0, 0, 1, 7, 2, 5, 8, 16, 3, 19, 6, 14, 9, 9, 17, 17, 4, 12, 20, 20, 7, 7, 15, 15, 10, 23, 10, 111, 18, 18, 18, 106, 5, 26, 13, 13, 21, 21, 21, 34, 8, 109, 8, 29, 16, 16, 16, 104, 11, 24, 24, 24, 11, 11, 112, 112, 19, 32, 19, 32, 19, 19, 107, 107, 6, 27, 27, 27, 14, 14, 14, 102, 22, 115, 22, 14, 22, 22, 35, 35, 9, 22, 110, 110, 9, 9, 30, 30, 17, 30, 17, 92, 17, 17, 105, 105, 12, 118, 25, 25, 25, 25, 25, 87, 12, 38, 12, 100, 113, 113, 113, 69, 20, 12, 33, 33, 20, 20, 33, 33, 20, 95, 20, 46, 108, 108, 108, 46, 7, 121, 28, 28, 28, 28, 28, 41, 15, 90, 15, 41, 15, 15, 103, 103, 23, 116, 116, 116, 23, 23, 15, 15, 23, 36, 23, 85, 36, 36, 36, 54, 10, 98, 23, 23, 111, 111, 111, 67, 10, 49, 10, 124, 31, 31, 31, 80, 18, 31, 31, 31, 18, 18, 93, 93, 18, 44, 18, 44, 106, 106, 106, 44, 13, 119, 119, 119, 26, 26, 26, 119, 26, 18, 26, 39, 26, 26, 88, 88, 13, 39, 39, 39, 13, 13, 101, 101, 114, 26, 114, 52, 114, 114, 70, 70, 21, 52, 13, 13, 34, 34, 34, 127, 21, 83, 21, 127, 34, 34, 34, 52, 21, 21, 96, 96, 21, 21, 47, 47, 109, 47, 109, 65, 109, 109, 47, 47, 8, 122, 122, 122, 29, 29, 29, 78, 29, 122, 29, 21, 29, 29, 42, 42, 16, 29, 91, 91, 16, 16, 42, 42, 16, 42, 16, 60, 104, 104, 104, 42, 24, 29, 117, 117, 117, 117, 117, 55, 24, 73, 24, 117, 16, 16, 16, 42, 24, 37, 37, 37, 24, 24, 86, 86, 37, 130, 37, 37, 37, 37, 55, 55, 11, 24, 99, 99, 24, 24, 24, 143, 112, 50, 112, 24, 112, 112, 68, 68, 11, 112, 50, 50, 11, 11, 125, 125, 32, 125, 32, 125, 32, 32, 81, 81, 19, 125, 32, 32, 32, 32, 32, 50, 19, 45, 19, 45, 94, 94, 94, 45, 19, 19, 45, 45, 19, 19, 45, 45, 107, 63, 107, 58, 107, 107, 45, 45, 14, 32, 120, 120, 120, 120, 120, 120, 27, 58, 27, 76, 27, 27, 120, 120, 27, 19, 19, 19, 27, 27, 40, 40, 27, 40, 27, 133, 89, 89, 89, 133, 14, 133, 40, 40, 40, 40, 40, 32, 14, 58, 14, 53, 102, 102, 102, 40, 115, 27, 27, 27, 115, 115, 53, 53, 115, 27, 115, 53, 71, 71, 71, 97, 22, 115, 53, 53, 14, 14, 14, 40, 35, 128, 35, 128, 35, 35, 128, 128, 22, 35, 84, 84, 22, 22, 128, 128, 35, 35, 35, 27, 35, 35, 53, 53, 22, 48, 22, 22, 97, 97, 97, 141, 22, 48, 22, 141, 48, 48, 48, 97, 110, 22, 48, 48, 110]
```
