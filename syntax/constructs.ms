/*
Showcase of basic programming constructs.
*/

# Block of code can be placed within curly braces
{ 
    txt = "some text" 
    out.println(txt)
}
out.println(txt) # Throws an error, since txt is out of scope

# If statements
a = true
b = false

if (a == b || b == false) {
    out.println("matched 1st if.")
} elif (a = true) {
    out.println("matched 2nd if.")
} else {
    out.println("fell in else.")
}

# Braces can be left out if there is only 1 expression
if (a == b) 
    out.println("a == b") 
else 
    out.println("a != b")

# Ternary if
c = (a == b) ? 42 : nil

# Loops
while (c != 42) {
    c = random.int(0, 100)
}

for(a : [1, 2, 3]) {
    a+"-"  # prints "1-2-3-"
}

for(a : 1,3..8) {
    if(a == 3) 
        continue
    print(a+",")  # prints "1,5,7,"
}

do {
    c = random.int(0, 100)
} while(c != 42)

# Functions
fun foo(arg1, arg2) {
    return arg1 + arg2
}

# Simple functions
fun bar(arg1, arg2) = arg1 + arg2

# Procedures
fun bas(arg1) {
    print(arg1) 
}

a = bas(42)  # Since the function has no return implicit nil value will be assigned to a